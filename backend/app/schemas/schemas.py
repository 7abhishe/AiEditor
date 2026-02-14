"""
CodeGenie AI Editor — Pydantic Schemas
Request/response models for API endpoints.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── API Key Schemas ──────────────────────────────────────

class APIKeyCreate(BaseModel):
    """Request to create a new API key."""
    label: str = Field(default="default", max_length=100, description="Human-readable label for this key")


class APIKeyResponse(BaseModel):
    """Response after creating an API key (only time plaintext key is shown)."""
    key_id: str
    api_key: str  # Plaintext — shown only once!
    label: str
    created_at: datetime

    class Config:
        from_attributes = True


class APIKeyInfo(BaseModel):
    """Public info about an API key (no secret)."""
    key_id: str
    label: str
    permissions: str
    is_active: bool
    created_at: datetime
    last_used_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        from_attributes = True


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
