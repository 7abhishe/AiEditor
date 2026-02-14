"""
CodeGenie AI Editor — API Key Management Endpoints
POST /api/v1/auth/keys    — Generate a new API key
GET  /api/v1/auth/keys    — List all keys (master key required)
DELETE /api/v1/auth/keys/{key_id} — Revoke a key
"""

import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.api_key_auth import hash_api_key
from app.models.models import APIKey
from app.schemas.schemas import APIKeyCreate, APIKeyResponse, APIKeyInfo

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/keys", response_model=APIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    payload: APIKeyCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a new API key.
    Returns the plaintext key — this is the ONLY time it will be shown.
    """
    # Generate a secure random API key
    raw_key = f"cg_{secrets.token_urlsafe(32)}"
    key_hash = hash_api_key(raw_key)

    # Create and save
    db_key = APIKey(
        key_hash=key_hash,
        label=payload.label,
    )
    db.add(db_key)
    await db.flush()
    await db.refresh(db_key)

    return APIKeyResponse(
        key_id=db_key.id,
        api_key=raw_key,
        label=db_key.label,
        created_at=db_key.created_at,
    )


@router.get("/keys", response_model=list[APIKeyInfo])
async def list_api_keys(
    master_key: str = None,
    db: AsyncSession = Depends(get_db),
):
    """
    List all API keys (requires master key via query param).
    Does not expose the actual key values.
    """
    if master_key != settings.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid master key. Pass ?master_key=<your-master-key>",
        )

    result = await db.execute(select(APIKey).order_by(APIKey.created_at.desc()))
    keys = result.scalars().all()

    return [
        APIKeyInfo(
            key_id=k.id,
            label=k.label,
            permissions=k.permissions,
            is_active=k.is_active,
            created_at=k.created_at,
            last_used_at=k.last_used_at,
            expires_at=k.expires_at,
        )
        for k in keys
    ]


@router.delete("/keys/{key_id}", status_code=status.HTTP_200_OK)
async def revoke_api_key(
    key_id: str,
    master_key: str = None,
    db: AsyncSession = Depends(get_db),
):
    """Revoke (deactivate) an API key."""
    if master_key != settings.master_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid master key.",
        )

    result = await db.execute(select(APIKey).where(APIKey.id == key_id))
    db_key = result.scalar_one_or_none()

    if not db_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"API key {key_id} not found.",
        )

    db_key.is_active = False
    await db.commit()

    return {"message": f"API key '{db_key.label}' has been revoked.", "key_id": key_id}
