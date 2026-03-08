"""
CodeGenie AI Editor — Authentication Endpoints
Handles user registration, OAuth2 login, and token refresh.
Security-hardened with rate limiting and input validation.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, get_password_hash, verify_password
from app.core.rate_limit import limiter
from app.core.auth import get_current_user
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


def _validate_email(email: str) -> str:
    """Validate and sanitize email input — reject null bytes and suspicious chars."""
    # Reject null bytes
    if "\x00" in email or "\0" in email:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email: contains null bytes",
        )
    # Reject unicode homoglyphs (basic check for non-ASCII in local part)
    local_part = email.split("@")[0] if "@" in email else email
    try:
        local_part.encode("ascii")
    except UnicodeEncodeError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid email: contains non-ASCII characters",
        )
    return email.strip().lower()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def signup(
    request: Request,
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user account.
    Rate limited to 5 signups per minute per IP.
    """
    # Sanitize and validate email
    clean_email = _validate_email(user_data.email)

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == clean_email))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash password and create user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=clean_email,
        hashed_password=hashed_password,
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 compatible token login, getting an access token for future requests.
    Rate limited to 10 login attempts per minute per IP.
    """
    # Find user by email (OAuth2 form uses 'username' field for the email)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account",
        )

    # Create JWT token containing the user's ID
    access_token = create_access_token(subject=user.id)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_user),
):
    """
    Refresh an access token. Requires a valid (non-expired) existing token.
    Issues a new token with a fresh expiry.
    """
    new_access_token = create_access_token(subject=current_user.id)
    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
