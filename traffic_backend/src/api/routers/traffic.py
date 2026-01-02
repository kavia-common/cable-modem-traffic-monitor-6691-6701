"""API routes for historical stats and realtime streaming."""

from __future__ import annotations

import asyncio
import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.deps import get_db_session
from src.schemas.traffic import Granularity, StatsResponse, TrafficPointOut
from src.services import modems as modem_service
from src.services import stats as stats_service
from src.settings import settings

router = APIRouter(prefix="/modems", tags=["Traffic"])


def _parse_dt(value: str) -> dt.datetime:
    # Accept ISO8601; allow trailing Z.
    v = value.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(v)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


@router.get(
    "/{modem_id}/stats",
    response_model=StatsResponse,
    summary="Get historical stats",
    description="Return aggregated traffic stats for a modem in the requested time range and granularity.",
    operation_id="get_modem_stats",
)
async def get_modem_stats(
    modem_id: int,
    from_: str = Query(..., alias="from", description="ISO8601 start timestamp"),
    to: str = Query(..., description="ISO8601 end timestamp"),
    granularity: Granularity = Query(..., description="Bucket size: 1m, 5m, or 1h"),
    session: AsyncSession = Depends(get_db_session),
) -> StatsResponse:
    """Get aggregated historical traffic stats for a modem."""
    modem = await modem_service.get_modem(session, modem_id)
    if modem is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Modem not found")

    from_ts = _parse_dt(from_)
    to_ts = _parse_dt(to)
    if to_ts <= from_ts:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="'to' must be after 'from'")

    rows = await stats_service.get_aggregated_points(session, modem_id, from_ts, to_ts, granularity)
    points = [TrafficPointOut(timestamp=ts, up_bps=up, down_bps=down) for ts, up, down in rows]

    return StatsResponse(
        modem_id=modem_id,
        granularity=granularity,
        from_ts=from_ts,
        to_ts=to_ts,
        points=points,
    )


@router.websocket(
    "/{modem_id}/realtime",
)
async def modem_realtime(websocket: WebSocket, modem_id: int) -> None:
    """
    WebSocket endpoint that streams traffic rates.

    Sends JSON messages like:
      {"timestamp": "...", "up_bps": 123, "down_bps": 456}

    Emission interval is ~REALTIME_EMIT_SECONDS.
    """
    await websocket.accept()

    # Validate modem exists using a one-off session.
    sessionmaker = None
    try:
        from src.db import get_sessionmaker as _gsm

        sessionmaker = _gsm()
        async with sessionmaker() as session:
            modem = await modem_service.get_modem(session, modem_id)
            if modem is None:
                await websocket.close(code=1008)  # policy violation / invalid request
                return
    except Exception:
        await websocket.close(code=1011)
        return

    # Stream by polling latest sample from DB.
    try:
        while True:
            async with sessionmaker() as session:
                # Query latest sample.
                from sqlalchemy import select
                from src.models.traffic_sample import TrafficSample

                res = await session.execute(
                    select(TrafficSample)
                    .where(TrafficSample.modem_id == modem_id)
                    .order_by(TrafficSample.timestamp.desc())
                    .limit(1)
                )
                sample = res.scalar_one_or_none()

            payload = {
                "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(),
                "up_bps": int(sample.up_bps) if sample else 0,
                "down_bps": int(sample.down_bps) if sample else 0,
            }
            await websocket.send_json(payload)
            await asyncio.sleep(settings.REALTIME_EMIT_SECONDS)
    except WebSocketDisconnect:
        return
    except Exception:
        # Best-effort close on server error.
        try:
            await websocket.close(code=1011)
        except Exception:
            pass
