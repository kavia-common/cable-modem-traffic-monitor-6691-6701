"""API routes for modem CRUD."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db_session
from src.schemas.modem import ModemCreate, ModemOut, ModemUpdate
from src.services import modems as modem_service

router = APIRouter(prefix="/modems", tags=["Modems"])


@router.post(
    "",
    response_model=ModemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create modem",
    description="Register a new modem to be monitored.",
    operation_id="create_modem",
)
async def create_modem(payload: ModemCreate, session: AsyncSession = Depends(get_db_session)) -> ModemOut:
    """Create a new modem."""
    modem = await modem_service.create_modem(session, payload)
    return ModemOut.model_validate(modem)


@router.get(
    "",
    response_model=list[ModemOut],
    summary="List modems",
    description="Return all registered modems.",
    operation_id="list_modems",
)
async def list_modems(session: AsyncSession = Depends(get_db_session)) -> list[ModemOut]:
    """List modems."""
    modems = await modem_service.list_modems(session)
    return [ModemOut.model_validate(m) for m in modems]


@router.get(
    "/{modem_id}",
    response_model=ModemOut,
    summary="Get modem",
    description="Fetch a single modem by id.",
    operation_id="get_modem",
)
async def get_modem(modem_id: int, session: AsyncSession = Depends(get_db_session)) -> ModemOut:
    """Get modem by ID."""
    modem = await modem_service.get_modem(session, modem_id)
    if modem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modem not found")
    return ModemOut.model_validate(modem)


@router.put(
    "/{modem_id}",
    response_model=ModemOut,
    summary="Update modem",
    description="Update an existing modem.",
    operation_id="update_modem",
)
async def update_modem(modem_id: int, payload: ModemUpdate, session: AsyncSession = Depends(get_db_session)) -> ModemOut:
    """Update modem by ID."""
    modem = await modem_service.get_modem(session, modem_id)
    if modem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modem not found")
    modem = await modem_service.update_modem(session, modem, payload)
    return ModemOut.model_validate(modem)


@router.delete(
    "/{modem_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete modem",
    description="Delete an existing modem and all of its samples.",
    operation_id="delete_modem",
)
async def delete_modem(modem_id: int, session: AsyncSession = Depends(get_db_session)) -> None:
    """Delete modem by ID."""
    deleted = await modem_service.delete_modem(session, modem_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modem not found")
    return None
