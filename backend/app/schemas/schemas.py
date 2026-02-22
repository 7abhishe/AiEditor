"""
CodeGenie AI Editor — Pydantic Schemas
Request/response models for API endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Auth & User Schemas ──────────────────────────────────────

class UserCreate(BaseModel):
    """Request to create a new user account."""
    email: str = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, description="User's password")


class UserResponse(BaseModel):
    """Response showing public user details."""
    id: str
    email: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Response when successfully authenticated."""
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Data stored inside the JWT."""
    user_id: Optional[str] = None


# ── Chat Schemas ─────────────────────────────────────────

class ChatRequest(BaseModel):
    """Request to chat with Gemini AI."""
    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: Optional[str] = Field(None, description="Existing conversation ID to continue")
    context: Optional[str] = Field(None, description="Additional code context")


class ChatResponse(BaseModel):
    """Response from AI chat."""
    response: str
    conversation_id: str
    model: str


# ── Common Schemas ───────────────────────────────────────

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = "ok"
    app_name: str
    version: str = "0.1.0"


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
