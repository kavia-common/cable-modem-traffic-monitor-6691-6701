"""Schemas for historical and realtime traffic data."""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, Field, conint


Granularity = Literal["1m", "5m", "1h"]


class TrafficSampleOut(BaseModel):
    """Single raw traffic sample."""

    timestamp: dt.datetime = Field(..., description="Sample timestamp (UTC).")
    up_bps: conint(ge=0) = Field(..., description="Upload rate in bits per second.")
    down_bps: conint(ge=0) = Field(..., description="Download rate in bits per second.")


class TrafficPointOut(BaseModel):
    """Aggregated traffic point for a time bucket."""

    timestamp: dt.datetime = Field(..., description="Bucket timestamp (UTC, bucket start).")
    up_bps: conint(ge=0) = Field(..., description="Aggregated upload bps for the bucket (average).")
    down_bps: conint(ge=0) = Field(..., description="Aggregated download bps for the bucket (average).")


class StatsResponse(BaseModel):
    """Response for historical stats."""

    modem_id: int = Field(..., description="Modem ID.")
    granularity: Granularity = Field(..., description="Bucket granularity.")
    from_ts: dt.datetime = Field(..., description="Query start timestamp (UTC).")
    to_ts: dt.datetime = Field(..., description="Query end timestamp (UTC).")
    points: list[TrafficPointOut] = Field(..., description="Aggregated points sorted by timestamp.")
