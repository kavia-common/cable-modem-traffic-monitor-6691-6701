"""Service functions for historical traffic stats queries."""

from __future__ import annotations

import datetime as dt

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.traffic_sample import TrafficSample
from src.schemas.traffic import Granularity


def _bucket_seconds(granularity: Granularity) -> int:
    if granularity == "1m":
        return 60
    if granularity == "5m":
        return 300
    if granularity == "1h":
        return 3600
    raise ValueError("Unsupported granularity")


def _normalize_range(from_ts: dt.datetime, to_ts: dt.datetime) -> tuple[dt.datetime, dt.datetime]:
    if from_ts.tzinfo is None:
        from_ts = from_ts.replace(tzinfo=dt.timezone.utc)
    if to_ts.tzinfo is None:
        to_ts = to_ts.replace(tzinfo=dt.timezone.utc)
    return from_ts.astimezone(dt.timezone.utc), to_ts.astimezone(dt.timezone.utc)


# PUBLIC_INTERFACE
async def get_aggregated_points(
    session: AsyncSession,
    modem_id: int,
    from_ts: dt.datetime,
    to_ts: dt.datetime,
    granularity: Granularity,
) -> list[tuple[dt.datetime, int, int]]:
    """
    Return list of (bucket_ts, avg_up_bps, avg_down_bps) ordered by bucket_ts.

    Implementation uses SQLite-compatible bucketing via unixepoch arithmetic.
    """
    from_ts, to_ts = _normalize_range(from_ts, to_ts)
    bucket = _bucket_seconds(granularity)

    # SQLite: strftime('%s', timestamp) gives unix seconds.
    # bucket_start = (unix // bucket) * bucket
    unix = func.strftime("%s", TrafficSample.timestamp)
    bucket_start_unix = (func.cast(unix, func.INTEGER) / bucket)
    bucket_start_unix = func.cast(bucket_start_unix, func.INTEGER) * bucket

    bucket_dt = func.datetime(bucket_start_unix, "unixepoch")

    q = (
        select(
            bucket_dt.label("bucket_ts"),
            func.avg(TrafficSample.up_bps).label("avg_up"),
            func.avg(TrafficSample.down_bps).label("avg_down"),
        )
        .where(
            and_(
                TrafficSample.modem_id == modem_id,
                TrafficSample.timestamp >= from_ts,
                TrafficSample.timestamp <= to_ts,
            )
        )
        .group_by("bucket_ts")
        .order_by("bucket_ts")
    )

    res = await session.execute(q)
    rows = []
    for bucket_ts, avg_up, avg_down in res.all():
        # bucket_ts from SQLite comes as string "YYYY-MM-DD HH:MM:SS"
        if isinstance(bucket_ts, str):
            parsed = dt.datetime.fromisoformat(bucket_ts).replace(tzinfo=dt.timezone.utc)
        else:
            parsed = bucket_ts
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=dt.timezone.utc)

        rows.append((parsed, int(avg_up or 0), int(avg_down or 0)))
    return rows
