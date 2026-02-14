"""
CodeGenie AI Editor — Git API Endpoints
Provides REST endpoints for Git operations.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from app.core.api_key_auth import get_current_api_key
from app.models.models import APIKey
from app.services.git_service import git_service

router = APIRouter(prefix="/git", tags=["git"])


# ── Request / Response Schemas ─────────────────────────────

class SetProjectRequest(BaseModel):
    project_path: str = Field(..., description="Absolute path to the project root")


class CommitRequest(BaseModel):
    message: str | None = Field(None, description="Commit message. If empty, AI generates one.")


class CheckoutRequest(BaseModel):
    branch: str = Field(..., description="Branch name to checkout")


class StageRequest(BaseModel):
    file_path: str = Field(..., description="File path to stage/unstage (relative to project root)")
    action: str = Field("stage", description="'stage' or 'unstage'")


# ── Endpoints ──────────────────────────────────────────────

@router.post("/project")
async def set_project(
    req: SetProjectRequest,
    current_key: APIKey = Depends(get_current_api_key),
):
    """Set the active project path for Git operations."""
    git_service.set_project_path(req.project_path)

    is_repo = await git_service.is_git_repo()
    if not is_repo:
        raise HTTPException(status_code=400, detail=f"Not a git repository: {req.project_path}")

    return {"project_path": req.project_path, "is_git_repo": True}


@router.get("/status")
async def get_status(
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Get the working tree status (modified, staged, untracked files)."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        files = await git_service.get_status()
        return {
            "files": files,
            "total": len(files),
            "staged": sum(1 for f in files if f['staged']),
            "unstaged": sum(1 for f in files if not f['staged']),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git status failed: {str(e)}")


@router.get("/diff")
async def get_diff(
    file_path: str | None = Query(None, description="Specific file to diff"),
    staged: bool = Query(False, description="Show staged changes"),
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Get the diff for working tree changes."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        diff = await git_service.get_diff(file_path=file_path, staged=staged)
        return {"diff": diff, "file_path": file_path, "staged": staged}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git diff failed: {str(e)}")


@router.get("/log")
async def get_log(
    count: int = Query(20, ge=1, le=100, description="Number of commits to fetch"),
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Get recent commit history."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        commits = await git_service.get_log(count=count)
        return {"commits": commits, "total": len(commits)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git log failed: {str(e)}")


@router.get("/branches")
async def get_branches(
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Get list of branches."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        branches = await git_service.get_branches()
        current = next((b['name'] for b in branches if b['is_current']), None)
        return {"branches": branches, "current": current}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git branches failed: {str(e)}")


@router.post("/commit")
async def commit_changes(
    req: CommitRequest,
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Commit changes. If no message provided, AI generates one from the diff."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        message = req.message
        ai_generated = False

        if not message:
            message = await git_service.ai_commit_message()
            ai_generated = True

        result = await git_service.commit(message)
        return {
            "message": message,
            "ai_generated": ai_generated,
            "output": result['output'],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git commit failed: {str(e)}")


@router.post("/checkout")
async def checkout_branch(
    req: CheckoutRequest,
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Switch to a different branch."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        result = await git_service.checkout(req.branch)
        return {"branch": req.branch, "output": result['output']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git checkout failed: {str(e)}")


@router.post("/stage")
async def stage_file(
    req: StageRequest,
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Stage or unstage a specific file."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        if req.action == "stage":
            await git_service.stage_file(req.file_path)
        elif req.action == "unstage":
            await git_service.unstage_file(req.file_path)
        else:
            raise HTTPException(status_code=400, detail="action must be 'stage' or 'unstage'")

        return {"file_path": req.file_path, "action": req.action, "success": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Git stage failed: {str(e)}")


@router.post("/ai-message")
async def generate_ai_commit_message(
    project_path: str | None = Query(None, description="Optional project path override"),
    current_key: APIKey = Depends(get_current_api_key),
):
    """Generate an AI commit message from the current diff without committing."""
    if project_path:
        git_service.set_project_path(project_path)

    try:
        message = await git_service.ai_commit_message()
        return {"message": message}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI message generation failed: {str(e)}")
