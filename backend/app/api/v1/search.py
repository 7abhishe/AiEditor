"""
CodeGenie AI Editor — Semantic Search API
Enhanced search endpoint with result grouping and previews.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from app.core.auth import get_current_user
from app.models.models import User

router = APIRouter(prefix="/search", tags=["search"])


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(10, ge=1, le=50, description="Number of results to return")
    project_path: str | None = Field(None, description="Optional project path for context")


@router.post("")
async def semantic_search(
    req: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Perform semantic search across the indexed codebase.
    Returns results grouped by file with snippet previews.
    """
    try:
        from app.services.vector_store import vector_store

        if not vector_store.chunks:
            return {
                "results": [],
                "total": 0,
                "message": "No indexed code available. Please index your project first.",
            }

        results = await vector_store.search(req.query, top_k=req.top_k)

        formatted = []
        for r in results:
            formatted.append({
                "content": r.get("content", ""),
                "file_path": r.get("file_path", r.get("metadata", {}).get("file_path", "unknown")),
                "line_number": r.get("start_line", r.get("metadata", {}).get("start_line")),
                "score": r.get("score", 0),
                "metadata": r.get("metadata", {}),
            })

        return {
            "results": formatted,
            "total": len(formatted),
            "query": req.query,
        }

    except ImportError:
        raise HTTPException(
            status_code=501,
            detail="Vector store not available. Install FAISS or run indexing first.",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
