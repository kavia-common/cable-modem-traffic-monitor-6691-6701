"""Service functions for modem CRUD."""

from __future__ import annotations

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.modem import Modem
from src.schemas.modem import ModemCreate, ModemUpdate


# PUBLIC_INTERFACE
async def create_modem(session: AsyncSession, payload: ModemCreate) -> Modem:
    """Create and persist a modem."""
    modem = Modem(name=payload.name, ip=str(payload.ip), status=payload.status)
    session.add(modem)
    await session.commit()
    await session.refresh(modem)
    return modem


# PUBLIC_INTERFACE
async def list_modems(session: AsyncSession) -> list[Modem]:
    """List all modems."""
    res = await session.execute(select(Modem).order_by(Modem.id.asc()))
    return list(res.scalars().all())


# PUBLIC_INTERFACE
async def get_modem(session: AsyncSession, modem_id: int) -> Modem | None:
    """Get modem by ID; returns None if missing."""
    res = await session.execute(select(Modem).where(Modem.id == modem_id))
    return res.scalar_one_or_none()


# PUBLIC_INTERFACE
async def update_modem(session: AsyncSession, modem: Modem, payload: ModemUpdate) -> Modem:
    """Update modem fields and persist."""
    if payload.name is not None:
        modem.name = payload.name
    if payload.ip is not None:
        modem.ip = str(payload.ip)
    if payload.status is not None:
        modem.status = payload.status

    session.add(modem)
    await session.commit()
    await session.refresh(modem)
    return modem


# PUBLIC_INTERFACE
async def delete_modem(session: AsyncSession, modem_id: int) -> bool:
    """Delete modem by ID; returns True if deleted."""
    res = await session.execute(delete(Modem).where(Modem.id == modem_id))
    await session.commit()
    return (res.rowcount or 0) > 0
