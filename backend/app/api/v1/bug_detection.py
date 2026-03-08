"""
CodeGenie AI Editor — Bug Detection Endpoint
POST /api/v1/bugs/detect — Analyze code for bugs, security issues, and anti-patterns.
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.rate_limit import limiter
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.models.models import User
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter(prefix="/bugs", tags=["Bug Detection"])


class BugDetectRequest(BaseModel):
    code: str = Field(..., description="Code to analyze")
    language: str = Field("", description="Programming language")
    file_path: str = Field("", description="File path for context")


class Bug(BaseModel):
    line: int = Field(0, description="Approximate line number")
    severity: str = Field("warning", description="low, warning, error, critical")
    category: str = Field("", description="Bug category (e.g., logic, security, performance)")
    description: str = Field("", description="What the bug is")
    suggestion: str = Field("", description="How to fix it")


class BugDetectResponse(BaseModel):
    bugs: list[Bug]
    summary: str
    model: str


@router.post("/detect", response_model=BugDetectResponse)
@limiter.limit("30/minute")
async def detect_bugs(
    request: Request,
    payload: BugDetectRequest,
    current_user: User = Depends(get_current_user),
):
    """Analyze code for bugs, security issues, and anti-patterns."""
    try:
        lang_hint = f" {payload.language}" if payload.language else ""
        prompt = f"""Analyze the following{lang_hint} code for bugs, security vulnerabilities, and anti-patterns.

Return your analysis as a structured JSON object with this exact format:
{{
  "bugs": [
    {{
      "line": <approximate line number>,
      "severity": "<low|warning|error|critical>",
      "category": "<logic|security|performance|style|memory|concurrency|error-handling>",
      "description": "<clear description of the issue>",
      "suggestion": "<how to fix it>"
    }}
  ],
  "summary": "<1-2 sentence overall assessment>"
}}

If no bugs found, return {{"bugs": [], "summary": "No issues detected."}}.

IMPORTANT: Return ONLY the JSON object, no markdown, no code fences.

Code:
```{payload.language}
{payload.code}
```"""

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt=(
                "You are CodeGenie, an expert code reviewer and static analysis tool. "
                "You find real bugs, not style nitpicks. Focus on logic errors, security vulnerabilities, "
                "resource leaks, race conditions, and potential crashes. Be precise about line numbers."
            ),
        )

        # Parse the JSON response
        import json
        try:
            # Clean up response — strip markdown fences if present
            clean = response.strip()
            if clean.startswith("```"):
                lines = clean.split("\n")
                clean = "\n".join(lines[1:-1]) if lines[-1].strip() == "```" else "\n".join(lines[1:])
            data = json.loads(clean)
        except json.JSONDecodeError:
            # Fallback: return raw response as summary
            return BugDetectResponse(
                bugs=[],
                summary=response[:500],
                model=settings.gemini_model,
            )

        bugs = [Bug(**b) for b in data.get("bugs", [])]
        summary = data.get("summary", "Analysis complete.")

        return BugDetectResponse(
            bugs=bugs,
            summary=summary,
            model=settings.gemini_model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred. Please try again. (ref: {type(e).__name__})")
