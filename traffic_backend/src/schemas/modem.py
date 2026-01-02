"""Pydantic schemas for modem CRUD."""

from __future__ import annotations

import datetime as dt

from pydantic import BaseModel, Field, IPvAnyAddress


class ModemCreate(BaseModel):
    """Request schema for creating a modem."""

    name: str = Field(..., min_length=1, max_length=200, description="Display name for the modem.")
    ip: IPvAnyAddress = Field(..., description="IP address (IPv4 or IPv6) used to identify the modem.")
    status: str = Field(default="unknown", max_length=32, description="Current status label.")


class ModemUpdate(BaseModel):
    """Request schema for updating a modem."""

    name: str | None = Field(default=None, min_length=1, max_length=200, description="Display name.")
    ip: IPvAnyAddress | None = Field(default=None, description="IP address.")
    status: str | None = Field(default=None, max_length=32, description="Status label.")


class ModemOut(BaseModel):
    """Response schema for a modem."""

    id: int = Field(..., description="Modem ID.")
    name: str = Field(..., description="Display name.")
    ip: str = Field(..., description="IP address.")
    status: str = Field(..., description="Status label.")
    created_at: dt.datetime = Field(..., description="Creation timestamp (UTC).")

    model_config = {"from_attributes": True}
