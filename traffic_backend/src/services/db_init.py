"""
Database initialization and seeding.

Creates tables and ensures at least one modem exists (seed).
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine

from src.db import get_engine, get_sessionmaker
from src.models.base import Base
from src.models.modem import Modem


# PUBLIC_INTERFACE
async def init_db() -> None:
    """Create DB tables if missing and seed a default modem if none exist."""
    engine: AsyncEngine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        res = await session.execute(select(Modem.id).limit(1))
        existing = res.scalar_one_or_none()
        if existing is None:
            session.add(
                Modem(
                    name="Default Modem",
                    ip="192.168.100.1",
                    status="online",
                )
            )
            await session.commit()
