"""
CodeGenie AI Editor — Agent API Endpoints
Provides REST + SSE endpoints for the autonomous coding agent.
"""

import json
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from app.core.rate_limit import limiter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from app.core.auth import get_current_user
from app.models.models import User
from app.services.agent_service import agent_service

router = APIRouter(prefix="/agent", tags=["agent"])


class AgentRunRequest(BaseModel):
    goal: str = Field(..., description="The coding task for the agent to accomplish")
    project_path: str = Field(..., description="Absolute path to the project root")
    context: str | None = Field(None, description="Additional context or code snippet")


class AgentApproveRequest(BaseModel):
    task_id: str = Field(..., description="The agent task ID")
    approved: bool = Field(True, description="Whether to approve the pending changes")


@router.post("/run")
@limiter.limit("15/minute")
async def run_agent(
    request: Request,
    req: AgentRunRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Start an autonomous agent task.
    Returns a Server-Sent Events (SSE) stream with real-time progress updates.
    """
    async def event_stream():
        async for event in agent_service.run_task(
            goal=req.goal,
            project_path=req.project_path,
            context=req.context,
        ):
            event_type = event.get("event", "message")
            data = json.dumps(event.get("data", {}))
            yield f"event: {event_type}\ndata: {data}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/run-sync")
@limiter.limit("15/minute")
async def run_agent_sync(
    request: Request,
    req: AgentRunRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Run an agent task synchronously (returns final result).
    Useful for simpler tasks or when SSE is not needed.
    """
    events = []
    async for event in agent_service.run_task(
        goal=req.goal,
        project_path=req.project_path,
        context=req.context,
    ):
        events.append(event)

    # Return the final state
    final_event = events[-1] if events else {"event": "error", "data": {"error": "No events"}}
    return {
        "task": final_event.get("data", {}),
        "events": events,
        "event_count": len(events),
    }


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get the status of an agent task."""
    status = agent_service.get_task_status(task_id)
    if not status:
        raise HTTPException(status_code=404, detail=f"Task not found: {task_id}")
    return status
