"""
CodeGenie AI Editor — Repository Indexing Endpoints
POST /api/v1/index/start — Start indexing a project
GET  /api/v1/index/status — Check indexing progress
POST /api/v1/index/search — Semantic search over indexed code
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.models.models import User
from app.services.indexing_service import indexing_service
from app.services.vector_store import vector_store

router = APIRouter(prefix="/index", tags=["Repository Indexing"])


class IndexRequest(BaseModel):
    project_path: str = Field(..., description="Absolute path to the project folder")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Natural language search query")
    top_k: int = Field(5, description="Number of results to return")


class SearchResult(BaseModel):
    file_path: str
    line_start: int
    line_end: int
    language: str
    content: str
    score: float


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total_indexed: int


@router.post("/start")
async def start_indexing(
    payload: IndexRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Start indexing a project folder in the background."""
    import os
    if not os.path.isdir(payload.project_path):
        raise HTTPException(status_code=400, detail=f"Not a valid directory: {payload.project_path}")

    if indexing_service.is_indexing:
        return {"message": "Indexing already in progress", **indexing_service.get_progress()}

    # Try loading existing index first
    loaded = vector_store.load(payload.project_path)
    if loaded:
        return {
            "message": f"Loaded existing index ({vector_store.total_chunks} chunks). Re-indexing in background...",
            "total_chunks": vector_store.total_chunks,
        }

    # Run indexing in background
    background_tasks.add_task(indexing_service.index_project, payload.project_path)
    return {"message": "Indexing started", "project_path": payload.project_path}


@router.get("/status")
async def get_index_status(
    current_user: User = Depends(get_current_user),
):
    """Get current indexing progress."""
    progress = indexing_service.get_progress()
    progress["total_indexed_chunks"] = vector_store.total_chunks
    return progress


@router.post("/search", response_model=SearchResponse)
async def search_code(
    payload: SearchRequest,
    current_user: User = Depends(get_current_user),
):
    """Semantic search over indexed code chunks."""
    if vector_store.total_chunks == 0:
        raise HTTPException(status_code=400, detail="No indexed code. Run /api/v1/index/start first.")

    results = await vector_store.search(payload.query, top_k=payload.top_k)

    return SearchResponse(
        results=[SearchResult(**r) for r in results],
        total_indexed=vector_store.total_chunks,
    )
