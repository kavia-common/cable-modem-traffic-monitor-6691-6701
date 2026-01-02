"""
Application settings.

Environment variables:
- DB_URL: SQLAlchemy async DB URL (default: sqlite+aiosqlite:///./traffic.db)
- CORS_ORIGIN: allowed browser origin (default: http://localhost:3000)
- SAMPLE_INTERVAL_SECONDS: how often we generate a traffic sample per modem (default: 5)
- REALTIME_EMIT_SECONDS: websocket emit interval per connection (default: 1)
"""

from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings loaded from environment (.env supported by runtime)."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DB_URL: str = Field(default="sqlite+aiosqlite:///./traffic.db", description="SQLAlchemy async DB URL.")
    CORS_ORIGIN: str = Field(default="http://localhost:3000", description="Allowed CORS origin for the frontend.")
    SAMPLE_INTERVAL_SECONDS: int = Field(default=5, ge=1, le=3600, description="Sample persistence cadence.")
    REALTIME_EMIT_SECONDS: int = Field(default=1, ge=1, le=60, description="Realtime WS emit interval per connection.")


settings = Settings()
