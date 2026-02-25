"""
CodeGenie AI Editor — Application Settings
Loads configuration from .env file using pydantic-settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Root directory of the project (backend/../)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables / .env file."""

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────
    app_name: str = "CodeGenie AI Editor"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    port: int = 8000  # Render sets PORT env var
    debug: bool = False  # Default to False (safe for production)

    # ── Database ─────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./codegenie.db"

    @property
    def async_database_url(self) -> str:
        """Convert database URL to async-compatible format.

        Render.com provides: postgresql://user:pass@host/db
        SQLAlchemy needs:    postgresql+asyncpg://user:pass@host/db
        """
        url = self.database_url
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
        elif url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+asyncpg://", 1)
        return url

    # ── Redis ────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379"

    # ── Google Gemini ────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"

    # ── API Key Auth ─────────────────────────────────────
    master_api_key: str = "codegenie-master-key-change-me"

    # ── JWT Authentication ────────────────────────────────
    jwt_secret_key: str = "codegenie-jwt-secret-change-in-production"


settings = Settings()
