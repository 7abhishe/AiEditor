"""
CodeGenie AI Editor — FastAPI Application Entry Point
Security-hardened with rate limiting, CORS restrictions, and security headers.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.database import engine, Base
from app.core.rate_limit import limiter
from app.api.router import api_router
from app.schemas.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    Creates database tables on startup.
    """
    # ── Startup ──
    # Import models so SQLAlchemy knows about them
    import app.models.models  # noqa: F401

    # Create tables (with retry for multi-worker race conditions)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        # Tables may already exist from another worker or previous deploy
        print(f"⚠️  Table creation skipped (already exist): {type(e).__name__}")

    print("✅ CodeGenie AI Editor backend started successfully!")
    print(f"📡 Gemini Model: {settings.gemini_model}")
    # Mask password in database URL for logs
    db_display = settings.database_url.split("@")[-1] if "@" in settings.database_url else settings.database_url
    print(f"🗄️  Database: ...@{db_display}")

    yield

    # ── Shutdown ──
    await engine.dispose()
    print("👋 CodeGenie backend shut down.")


# ── Create FastAPI App ───────────────────────────────────
# Disable Swagger docs in production (only accessible when DEBUG=True)
app = FastAPI(
    title=settings.app_name,
    description="AI-powered code editor backend — powered by Google Gemini",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None,
)

# ── Rate Limiting ────────────────────────────────────────
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ── CORS Middleware (SECURITY FIX) ──────────────────────
# Restrict to known frontend origins only
allowed_origins = [
    "http://localhost:5173",           # Local Vite dev server
    "http://localhost:3000",           # Alternative local dev
    "https://codegenie-web.onrender.com",  # Production frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS", "HEAD"],
    allow_headers=["Authorization", "Content-Type", "X-API-Key"],
)


# ── Security Headers Middleware ─────────────────────────
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Prevent MIME-type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Prevent clickjacking
    response.headers["X-Frame-Options"] = "DENY"
    # Enforce HTTPS (1 year)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none'"
    # Prevent information leakage
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


# ── Request Body Size Limit Middleware ───────────────────
MAX_BODY_SIZE = 1 * 1024 * 1024  # 1MB

@app.middleware("http")
async def limit_request_size(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > MAX_BODY_SIZE:
        return JSONResponse(
            status_code=413,
            content={"detail": "Request body too large. Maximum size is 1MB."},
        )
    return await call_next(request)


# ── Mount API Router ─────────────────────────────────────
app.include_router(api_router)


# ── Health Check ─────────────────────────────────────────
@app.api_route("/", methods=["GET", "HEAD"], response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Root health check endpoint."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version="0.1.0",
    )


@app.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version="0.1.0",
    )
