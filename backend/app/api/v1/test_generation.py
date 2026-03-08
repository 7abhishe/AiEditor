"""
CodeGenie AI Editor — Test Generation Endpoint
POST /api/v1/tests/generate — Generate unit tests for given code.
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.rate_limit import limiter
from pydantic import BaseModel, Field

from app.core.auth import get_current_user
from app.models.models import User
from app.services.ai_service import ai_service
from app.core.config import settings

router = APIRouter(prefix="/tests", tags=["Test Generation"])

# Language → default test framework mapping
FRAMEWORK_MAP = {
    "python": "pytest",
    "javascript": "jest",
    "typescript": "jest",
    "java": "JUnit 5",
    "go": "testing",
    "rust": "built-in",
    "ruby": "RSpec",
    "csharp": "xUnit",
    "php": "PHPUnit",
    "swift": "XCTest",
    "kotlin": "JUnit 5",
}


class TestGenRequest(BaseModel):
    code: str = Field(..., description="Code to generate tests for")
    language: str = Field("", description="Programming language")
    framework: str = Field("", description="Test framework override (e.g., pytest, jest)")


class TestGenResponse(BaseModel):
    test_code: str
    framework: str
    test_count: int
    model: str


@router.post("/generate", response_model=TestGenResponse)
@limiter.limit("30/minute")
async def generate_tests(
    request: Request,
    payload: TestGenRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate unit tests for the given code."""
    try:
        # Determine framework
        framework = payload.framework or FRAMEWORK_MAP.get(payload.language, "appropriate")
        lang_hint = f" {payload.language}" if payload.language else ""

        prompt = f"""Generate comprehensive unit tests for the following{lang_hint} code using {framework}.

Requirements:
1. Test all public functions/methods
2. Cover edge cases (empty inputs, boundary values, error conditions)
3. Use descriptive test names that explain what's being tested
4. Include setup/teardown if needed
5. Add brief comments explaining each test's purpose
6. Generate the complete, runnable test file

Return your response as a JSON object:
{{
  "test_code": "<the complete test code>",
  "framework": "{framework}",
  "test_count": <number of test cases>
}}

IMPORTANT: Return ONLY the JSON object, no markdown, no code fences.

Code to test:
```{payload.language}
{payload.code}
```"""

        response = await ai_service.generate_response(
            message=prompt,
            system_prompt=(
                "You are CodeGenie, an expert test engineer. You write thorough, "
                "practical unit tests that catch real bugs. Focus on meaningful test cases "
                "rather than trivial ones. Always generate complete, runnable test files."
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
            # Fallback: treat entire response as test code
            return TestGenResponse(
                test_code=response,
                framework=framework,
                test_count=0,
                model=settings.gemini_model,
            )

        return TestGenResponse(
            test_code=data.get("test_code", response),
            framework=data.get("framework", framework),
            test_count=data.get("test_count", 0),
            model=settings.gemini_model,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An internal error occurred. Please try again. (ref: {type(e).__name__})")
