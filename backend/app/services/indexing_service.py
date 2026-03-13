"""
CodeGenie AI Editor — Repository Indexing Service
Walks project directories, chunks code files, and stores embeddings in FAISS.
"""

import os
import asyncio
from pathlib import Path
from datetime import datetime, timezone

from app.services.vector_store import vector_store

# File extensions to index (source code only)
INDEXABLE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp",
    ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".scala", ".cs",
    ".html", ".css", ".scss", ".less",
    ".json", ".yaml", ".yml", ".toml", ".xml",
    ".sql", ".sh", ".bash", ".md", ".txt",
}

# Directories to always skip
SKIP_DIRS = {
    "node_modules", ".git", ".venv", "venv", "__pycache__", ".codegenie",
    ".next", ".nuxt", "dist", "build", ".tox", ".mypy_cache", ".pytest_cache",
    "target", "bin", "obj", ".idea", ".vscode",
}

# Max file size to index (500KB)
MAX_FILE_SIZE = 500_000

# Extension → language mapping
EXT_TO_LANG = {
    ".py": "python", ".js": "javascript", ".jsx": "javascript",
    ".ts": "typescript", ".tsx": "typescript", ".java": "java",
    ".c": "c", ".cpp": "cpp", ".h": "c", ".hpp": "cpp",
    ".go": "go", ".rs": "rust", ".rb": "ruby", ".php": "php",
    ".swift": "swift", ".kt": "kotlin", ".scala": "scala", ".cs": "csharp",
    ".html": "html", ".css": "css", ".scss": "scss",
    ".json": "json", ".yaml": "yaml", ".yml": "yaml",
    ".sql": "sql", ".sh": "shell", ".md": "markdown",
}


class IndexingService:
    """Orchestrates project indexing — walking files, chunking, embedding."""

    def __init__(self):
        self.is_indexing = False
        self.progress = {
            "total_files": 0,
            "indexed_files": 0,
            "total_chunks": 0,
            "status": "idle",
            "current_file": "",
            "started_at": None,
            "completed_at": None,
        }

    def _collect_files(self, project_path: str) -> list[Path]:
        """Walk the project and collect indexable source files."""
        files = []
        root = Path(project_path)

        for dirpath, dirnames, filenames in os.walk(root):
            # Filter out skip directories in-place
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for filename in filenames:
                filepath = Path(dirpath) / filename
                ext = filepath.suffix.lower()

                if ext not in INDEXABLE_EXTENSIONS:
                    continue

                try:
                    if filepath.stat().st_size > MAX_FILE_SIZE:
                        continue
                except OSError:
                    continue

                files.append(filepath)

        return files

    def _chunk_file(self, filepath: Path, project_root: str) -> list[dict]:
        """
        Split a file into semantic code chunks.
        Strategy: chunk by logical blocks (functions, classes) where possible,
        fallback to fixed-size line windows.
        """
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            return []

        if not content.strip():
            return []

        ext = filepath.suffix.lower()
        language = EXT_TO_LANG.get(ext, "text")
        rel_path = str(filepath.relative_to(project_root))
        lines = content.split("\n")

        chunks = []

        # For Python, try function/class-level chunking
        if language == "python":
            chunks = self._chunk_python(lines, rel_path, language)

        # If language-specific chunking didn't produce results, use line-window fallback
        if not chunks:
            chunks = self._chunk_by_lines(lines, rel_path, language, window=60, overlap=10)

        return chunks

    def _chunk_python(self, lines: list[str], file_path: str, language: str) -> list[dict]:
        """Chunk Python code by top-level functions and classes."""
        chunks = []
        current_block = []
        block_start = 0
        in_block = False

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Detect top-level definition start
            if (stripped.startswith("def ") or stripped.startswith("class ") or
                    stripped.startswith("async def ")) and not line.startswith(" "):
                # Save previous block if exists
                if current_block and in_block:
                    chunk_text = "\n".join(current_block)
                    if len(chunk_text.strip()) > 20:
                        chunks.append({
                            "content": f"# File: {file_path}\n{chunk_text}",
                            "file_path": file_path,
                            "line_start": block_start + 1,
                            "line_end": i,
                            "language": language,
                        })

                current_block = [line]
                block_start = i
                in_block = True
            elif in_block:
                current_block.append(line)

        # Save last block
        if current_block and in_block:
            chunk_text = "\n".join(current_block)
            if len(chunk_text.strip()) > 20:
                chunks.append({
                    "content": f"# File: {file_path}\n{chunk_text}",
                    "file_path": file_path,
                    "line_start": block_start + 1,
                    "line_end": len(lines),
                    "language": language,
                })

        return chunks

    def _chunk_by_lines(
        self, lines: list[str], file_path: str, language: str,
        window: int = 60, overlap: int = 10,
    ) -> list[dict]:
        """Chunk code by fixed-size line windows with overlap."""
        chunks = []
        total = len(lines)

        if total <= window:
            chunk_text = "\n".join(lines)
            if len(chunk_text.strip()) > 20:
                chunks.append({
                    "content": f"// File: {file_path}\n{chunk_text}",
                    "file_path": file_path,
                    "line_start": 1,
                    "line_end": total,
                    "language": language,
                })
            return chunks

        start = 0
        while start < total:
            end = min(start + window, total)
            chunk_lines = lines[start:end]
            chunk_text = "\n".join(chunk_lines)

            if len(chunk_text.strip()) > 20:
                chunks.append({
                    "content": f"// File: {file_path}\n{chunk_text}",
                    "file_path": file_path,
                    "line_start": start + 1,
                    "line_end": end,
                    "language": language,
                })

            if end >= total:
                break
            start += window - overlap

        return chunks

    async def index_project(self, project_path: str) -> dict:
        """
        Index an entire project — collect files, chunk, embed, and store.
        Returns indexing summary.
        """
        if self.is_indexing:
            return {"error": "Indexing already in progress", **self.progress}

        self.is_indexing = True
        self.progress = {
            "total_files": 0,
            "indexed_files": 0,
            "total_chunks": 0,
            "status": "scanning",
            "current_file": "",
            "started_at": datetime.now(timezone.utc).isoformat(),
            "completed_at": None,
        }

        try:
            # Clear existing index
            vector_store.clear()

            # Collect files
            files = self._collect_files(project_path)
            self.progress["total_files"] = len(files)
            self.progress["status"] = "indexing"

            # Chunk all files
            all_chunks = []
            for i, filepath in enumerate(files):
                self.progress["current_file"] = str(filepath)
                self.progress["indexed_files"] = i + 1

                chunks = self._chunk_file(filepath, project_path)
                all_chunks.extend(chunks)

            self.progress["total_chunks"] = len(all_chunks)
            self.progress["status"] = "embedding"

            # Embed and store in batches
            batch_size = 50
            for i in range(0, len(all_chunks), batch_size):
                batch = all_chunks[i:i + batch_size]
                await vector_store.add_chunks(batch)
                # Allow event loop to breathe
                await asyncio.sleep(0)

            # Save to disk
            vector_store.save(project_path)

            self.progress["status"] = "complete"
            self.progress["completed_at"] = datetime.now(timezone.utc).isoformat()

            return self.progress

        except Exception as e:
            self.progress["status"] = f"error: {str(e)}"
            raise
        finally:
            self.is_indexing = False

    def get_progress(self) -> dict:
        """Return current indexing progress."""
        return self.progress


# Singleton
indexing_service = IndexingService()
