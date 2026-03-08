"""
CodeGenie AI Editor — Code Completion Endpoint
POST /api/v1/completion — Get inline code completion from Gemini
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.rate_limit import limiter
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.models.models import User
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter(prefix="/completion", tags=["Code Completion"])


class CompletionRequest(BaseModel):
    prefix: str = Field(..., description="Code before the cursor")
    suffix: str = Field("", description="Code after the cursor")
    language: str = Field("", description="Programming language")


class CompletionResponse(BaseModel):
    completion: str
    model: str


@router.post("", response_model=CompletionResponse)
@limiter.limit("30/minute")
async def get_completion(
    request: Request,
    payload: CompletionRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate inline code completion using Gemini."""
    try:
        prompt = (
            f"You are an expert code completion engine. Complete the following {payload.language} code. "
            f"Return ONLY the completion text — no explanation, no markdown, no code fences. "
            f"The completion should naturally continue from where the code ends.\n\n"
            f"Code before cursor:\n{payload.prefix}\n"
        )
        if payload.suffix:
            prompt += f"\nCode after cursor:\n{payload.suffix}\n"

        response = await ai_service.generate_response(message=prompt)

        # Clean up: remove code fences if model adds them
        completion = response.strip()
        if completion.startswith("```"):
            lines = completion.split("\n")
            completion = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])

        return CompletionResponse(
            completion=completion,
            model=settings.gemini_model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred. Please try again. (ref: {type(e).__name__})")
