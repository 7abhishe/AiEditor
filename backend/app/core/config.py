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
    debug: bool = True

    # ── Database ─────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./codegenie.db"

    # ── Redis ────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379"

    # ── Google Gemini ────────────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3-flash-preview"

    # ── API Key Auth ─────────────────────────────────────
    master_api_key: str = "codegenie-master-key-change-me"


settings = Settings()
