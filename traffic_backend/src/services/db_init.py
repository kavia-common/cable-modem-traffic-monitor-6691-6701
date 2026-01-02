"""
Database initialization.

Creates tables (no seed data).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine

from src.db import get_engine
from src.models.base import Base

# IMPORTANT:
# Import the models package so all ORM classes are registered before
# Base.metadata.create_all() and before any ORM query triggers mapper configuration.
import src.models  # noqa: F401


# PUBLIC_INTERFACE
async def init_db() -> None:
    """Create DB tables if missing.

    This function intentionally does NOT seed any default Modem rows
    (不需要 Modem 資料).
    """
    engine: AsyncEngine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
