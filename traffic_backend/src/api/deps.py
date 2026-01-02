"""FastAPI dependencies (DB session, etc.)."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_sessionmaker


# PUBLIC_INTERFACE
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an AsyncSession per request."""
    sessionmaker = get_sessionmaker()
    async with sessionmaker() as session:
        yield session
