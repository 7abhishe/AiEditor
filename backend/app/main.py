"""
CodeGenie AI Editor — FastAPI Application Entry Point
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import engine, Base
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

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

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
app = FastAPI(
    title=settings.app_name,
    description="AI-powered code editor backend — powered by Google Gemini",
    version="0.1.0",
    lifespan=lifespan,
)

# ── CORS Middleware ──────────────────────────────────────
# In production, restrict origins; in development, allow all
allowed_origins = ["*"] if settings.debug else [
    "https://codegenie-frontend.onrender.com",
    "http://localhost:5173",  # Local Electron dev
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Mount API Router ─────────────────────────────────────
app.include_router(api_router)


# ── Health Check ─────────────────────────────────────────
@app.get("/", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Root health check endpoint."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version="0.1.0",
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version="0.1.0",
    )
