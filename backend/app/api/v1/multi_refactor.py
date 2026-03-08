"""
CodeGenie AI Editor — Multi-file Refactoring API
Refactoring that spans multiple files using AI + FAISS context.
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from app.core.rate_limit import limiter
from pydantic import BaseModel, Field
from app.core.auth import get_current_user
from app.models.models import User
from app.services.ai_service import ai_service

router = APIRouter(prefix="/refactor", tags=["refactor-multi"])


class MultiRefactorRequest(BaseModel):
    instruction: str = Field(..., description="What to refactor (e.g., 'rename User class to Account')")
    files: list[dict] = Field(default_factory=list, description="List of {path, content} dicts for files to refactor")
    project_path: str | None = Field(None, description="Project root for FAISS context lookup")
    language: str = Field("", description="Programming language hint")


@router.post("/multi")
@limiter.limit("15/minute")
async def multi_file_refactor(
    request: Request,
    req: MultiRefactorRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Refactor across multiple files. Returns per-file diffs and refactored content.
    """
    if not req.files and not req.project_path:
        raise HTTPException(status_code=400, detail="Provide files or a project_path")

    # If no files provided but project_path is set, find related files via FAISS
    files = req.files
    if not files and req.project_path:
        try:
            from app.services.vector_store import vector_store
            results = await vector_store.search(req.instruction, top_k=5)
            seen = set()
            for r in results:
                fp = r.get("file_path", r.get("metadata", {}).get("file_path"))
                if fp and fp not in seen:
                    seen.add(fp)
                    try:
                        import os
                        full = os.path.join(req.project_path, fp) if not os.path.isabs(fp) else fp
                        with open(full, 'r', encoding='utf-8') as f:
                            content = f.read()
                        files.append({"path": fp, "content": content})
                    except Exception:
                        pass
        except Exception:
            pass

    if not files:
        raise HTTPException(status_code=400, detail="No files to refactor")

    # Build a context block of all files
    files_context = ""
    for f in files[:10]:  # limit to 10 files
        files_context += f"\n--- FILE: {f['path']} ---\n{f['content'][:3000]}\n"

    prompt = f"""You are a multi-file refactoring engine. Apply this refactoring instruction across ALL the files provided.

INSTRUCTION: {req.instruction}
LANGUAGE: {req.language or 'auto-detect'}

FILES:
{files_context}

Return a JSON array of refactored files. Each item should have:
- "path": the file path
- "original_snippet": a short snippet showing what changed (before)
- "refactored_snippet": the same snippet after refactoring
- "refactored_content": the COMPLETE refactored file content
- "changes_made": brief description of changes in this file

Return ONLY the JSON array."""

    try:
        response = await ai_service.generate_response(
            message=prompt,
            system_prompt="You are a precise multi-file refactoring engine. Return ONLY valid JSON."
        )

        # Parse response
        import json
        text = response.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1]
            if "```" in text:
                text = text[:text.rfind("```")]
        text = text.strip()

        results = json.loads(text)

        return {
            "refactored_files": results,
            "total_files": len(results),
            "instruction": req.instruction,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred. Please try again. (ref: {type(e).__name__})")
