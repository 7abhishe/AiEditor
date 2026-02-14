"""
CodeGenie AI Editor — Code Explanation Endpoint
POST /api/v1/explain — Explain selected code using Gemini
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.api_key_auth import get_current_api_key
from app.models.models import APIKey
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter(prefix="/explain", tags=["Code Explanation"])


class ExplainRequest(BaseModel):
    code: str = Field(..., description="Code to explain")
    language: str = Field("", description="Programming language")


class ExplainResponse(BaseModel):
    explanation: str
    model: str


@router.post("", response_model=ExplainResponse)
async def explain_code(
    payload: ExplainRequest,
    current_key: APIKey = Depends(get_current_api_key),
):
    """Explain selected code using Gemini AI."""
    try:
        lang_hint = f" ({payload.language})" if payload.language else ""
        prompt = (
            f"Explain the following{lang_hint} code clearly and concisely. "
            f"Break down what each part does, mention any patterns used, "
            f"and highlight potential issues if any.\n\n"
            f"```{payload.language}\n{payload.code}\n```"
        )

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt=(
                "You are CodeGenie, an AI coding assistant. "
                "Provide clear, educational explanations of code. "
                "Use markdown formatting with code examples when helpful."
            ),
        )

        return ExplainResponse(
            explanation=response,
            model=settings.gemini_model,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Explain error: {str(e)}")
