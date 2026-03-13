"""
CodeGenie AI Editor — FAISS Vector Store
Manages code embeddings for semantic search (RAG pipeline).
Uses Gemini text-embedding-004 for generating embeddings.
"""

import os
import json
import hashlib
import numpy as np
from pathlib import Path
from typing import Optional

from google import genai
from app.core.config import settings


class VectorStore:
    """FAISS-based vector store for code embeddings."""

    def __init__(self):
        self._client = None
        self._index = None
        self._metadata: list[dict] = []  # Maps vector index → {file_path, chunk, line_start, line_end}
        self._dimension = 768  # text-embedding-004 output dimension
        self._index_dir: Optional[Path] = None

    @property
    def client(self):
        if self._client is None:
            self._client = genai.Client(api_key=settings.gemini_api_key)
        return self._client

    def _ensure_faiss(self):
        """Lazy import FAISS to avoid startup cost if not used."""
        if self._index is None:
            try:
                import faiss
                self._index = faiss.IndexFlatIP(self._dimension)  # Inner Product (cosine after normalization)
            except ImportError:
                # Fallback: use a simple numpy-based similarity search
                self._index = None
                self._vectors = []

    # ── Embedding ────────────────────────────────────────

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts using Gemini."""
        if not texts:
            return []

        embeddings = []
        # Process in batches of 100 (API limit)
        batch_size = 100
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            result = self.client.models.embed_content(
                model="text-embedding-004",
                contents=batch,
            )
            for emb in result.embeddings:
                embeddings.append(emb.values)

        return embeddings

    async def embed_single(self, text: str) -> list[float]:
        """Generate embedding for a single text."""
        result = await self.embed_texts([text])
        return result[0] if result else []

    # ── Index Management ─────────────────────────────────

    async def add_chunks(self, chunks: list[dict]):
        """
        Add code chunks to the vector store.
        Each chunk: { "content": str, "file_path": str, "line_start": int, "line_end": int, "language": str }
        """
        self._ensure_faiss()

        texts = [c["content"] for c in chunks]
        embeddings = await self.embed_texts(texts)

        if not embeddings:
            return

        vectors = np.array(embeddings, dtype="float32")
        # L2-normalize for cosine similarity via inner product
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1
        vectors = vectors / norms

        try:
            import faiss
            if self._index is None:
                self._index = faiss.IndexFlatIP(self._dimension)
            self._index.add(vectors)
        except ImportError:
            # Numpy fallback
            if not hasattr(self, '_vectors'):
                self._vectors = []
            self._vectors.extend(vectors.tolist())

        # Store metadata
        for chunk in chunks:
            self._metadata.append({
                "file_path": chunk.get("file_path", ""),
                "line_start": chunk.get("line_start", 0),
                "line_end": chunk.get("line_end", 0),
                "language": chunk.get("language", ""),
                "content": chunk["content"],
                "content_hash": hashlib.md5(chunk["content"].encode()).hexdigest(),
            })

    async def search(self, query: str, top_k: int = 5) -> list[dict]:
        """Search for the most relevant code chunks given a query."""
        self._ensure_faiss()

        query_embedding = await self.embed_single(query)
        if not query_embedding:
            return []

        query_vec = np.array([query_embedding], dtype="float32")
        # Normalize
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm

        results = []

        try:
            import faiss  # noqa: F401
            if self._index is not None and self._index.ntotal > 0:
                k = min(top_k, self._index.ntotal)
                scores, indices = self._index.search(query_vec, k)
                for score, idx in zip(scores[0], indices[0]):
                    if idx < len(self._metadata):
                        result = {**self._metadata[idx], "score": float(score)}
                        results.append(result)
        except ImportError:
            # Numpy fallback
            if hasattr(self, '_vectors') and self._vectors:
                vectors = np.array(self._vectors, dtype="float32")
                scores = vectors @ query_vec.T
                scores = scores.flatten()
                top_indices = np.argsort(scores)[::-1][:top_k]
                for idx in top_indices:
                    if idx < len(self._metadata):
                        result = {**self._metadata[idx], "score": float(scores[idx])}
                        results.append(result)

        return results

    # ── Persistence ──────────────────────────────────────

    def save(self, project_path: str):
        """Save FAISS index and metadata to disk."""
        index_dir = Path(project_path) / ".codegenie"
        index_dir.mkdir(exist_ok=True)

        # Save metadata
        meta_path = index_dir / "index_metadata.json"
        with open(meta_path, "w") as f:
            json.dump(self._metadata, f, indent=2)

        # Save FAISS index
        try:
            import faiss
            if self._index is not None and self._index.ntotal > 0:
                faiss_path = str(index_dir / "faiss.index")
                faiss.write_index(self._index, faiss_path)
        except ImportError:
            # Save numpy vectors
            if hasattr(self, '_vectors') and self._vectors:
                np_path = index_dir / "vectors.npy"
                np.save(str(np_path), np.array(self._vectors, dtype="float32"))

        self._index_dir = index_dir

    def load(self, project_path: str) -> bool:
        """Load FAISS index and metadata from disk. Returns True if loaded."""
        index_dir = Path(project_path) / ".codegenie"
        meta_path = index_dir / "index_metadata.json"

        if not meta_path.exists():
            return False

        with open(meta_path) as f:
            self._metadata = json.load(f)

        try:
            import faiss
            faiss_path = str(index_dir / "faiss.index")
            if os.path.exists(faiss_path):
                self._index = faiss.read_index(faiss_path)
                self._index_dir = index_dir
                return True
        except ImportError:
            np_path = index_dir / "vectors.npy"
            if np_path.exists():
                self._vectors = np.load(str(np_path)).tolist()
                self._index_dir = index_dir
                return True

        return False

    @property
    def total_chunks(self) -> int:
        """Number of chunks in the store."""
        return len(self._metadata)

    def clear(self):
        """Clear all data from the store."""
        self._ensure_faiss()
        try:
            import faiss
            self._index = faiss.IndexFlatIP(self._dimension)
        except ImportError:
            self._vectors = []
        self._metadata = []


# Singleton instance
vector_store = VectorStore()
