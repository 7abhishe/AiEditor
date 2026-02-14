"""
CodeGenie AI Editor — Refactoring Engine Endpoint
POST /api/v1/refactor — Suggest code improvements with before/after diffs.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.api_key_auth import get_current_api_key
from app.models.models import APIKey
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter(prefix="/refactor", tags=["Refactoring"])


class RefactorRequest(BaseModel):
    code: str = Field(..., description="Code to refactor")
    language: str = Field("", description="Programming language")
    focus: str = Field("", description="Optional focus area: readability, performance, patterns, naming")


class Suggestion(BaseModel):
    title: str = Field("", description="Short title of the improvement")
    description: str = Field("", description="Why this change is beneficial")
    original_code: str = Field("", description="The original code snippet")
    refactored_code: str = Field("", description="The improved code snippet")


class RefactorResponse(BaseModel):
    suggestions: list[Suggestion]
    summary: str
    model: str


@router.post("", response_model=RefactorResponse)
async def refactor_code(
    payload: RefactorRequest,
    current_key: APIKey = Depends(get_current_api_key),
):
    """Suggest code improvements with before/after diffs."""
    try:
        lang_hint = f" {payload.language}" if payload.language else ""
        focus_hint = f" Focus especially on: {payload.focus}." if payload.focus else ""
        prompt = f"""Analyze the following{lang_hint} code and suggest refactoring improvements.{focus_hint}

Return your suggestions as a structured JSON object with this exact format:
{{
  "suggestions": [
    {{
      "title": "<short title>",
      "description": "<why this improvement matters>",
      "original_code": "<the original code being improved>",
      "refactored_code": "<the improved version>"
    }}
  ],
  "summary": "<1-2 sentence overall assessment>"
}}

Focus on meaningful improvements:
- Naming clarity
- Dead code removal
- Simplification and readability
- Design patterns
- Performance optimizations
- Error handling improvements
- DRY violations

IMPORTANT: Return ONLY the JSON object, no markdown, no code fences.

Code:
```{payload.language}
{payload.code}
```"""

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt=(
                "You are CodeGenie, a senior software engineer specializing in code refactoring. "
                "You suggest practical, high-impact improvements. Focus on code that can be meaningfully "
                "improved — don't suggest trivial changes. Show complete before/after code snippets."
            ),
        )

        import json
        try:
            clean = response.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
            data = json.loads(clean)
        except json.JSONDecodeError:
            return RefactorResponse(
                suggestions=[],
                summary=response[:500],
                model=settings.gemini_model,
            )

        suggestions = [Suggestion(**s) for s in data.get("suggestions", [])]
        summary = data.get("summary", "Refactoring analysis complete.")

        return RefactorResponse(
            suggestions=suggestions,
            summary=summary,
            model=settings.gemini_model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refactoring error: {str(e)}")
