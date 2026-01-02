"""
Database setup for the traffic monitor backend.

Uses SQLAlchemy async engine. Defaults to SQLite for local development, but can be
swapped via env var (see src/settings.py).
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from src.settings import settings

_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _create_engine() -> AsyncEngine:
    """
    Create the SQLAlchemy async engine.

    Note: this is kept internal; use get_engine() and get_sessionmaker().
    """
    return create_async_engine(
        settings.DB_URL,
        echo=False,
        future=True,
    )


# PUBLIC_INTERFACE
def get_engine() -> AsyncEngine:
    """Return the singleton AsyncEngine."""
    global _engine
    if _engine is None:
        _engine = _create_engine()
    return _engine


# PUBLIC_INTERFACE
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return the singleton async sessionmaker."""
    global _sessionmaker
    if _sessionmaker is None:
        _sessionmaker = async_sessionmaker(
            bind=get_engine(),
            expire_on_commit=False,
            class_=AsyncSession,
        )
    return _sessionmaker
