"""
Background sampling loop.

This simulates traffic samples for each registered modem with deterministic randomness
per modem (stable-ish patterns), and persists samples every N seconds.
"""

from __future__ import annotations

import asyncio
import datetime as dt
import random
from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_sessionmaker
from src.models.modem import Modem
from src.models.traffic_sample import TrafficSample
from src.settings import settings


@dataclass
class _State:
    stop_event: asyncio.Event
    task: asyncio.Task[None] | None = None


_state = _State(stop_event=asyncio.Event())


def _rng_for_modem(modem_id: int) -> random.Random:
    # Deterministic seed so each modem has stable random-ish evolution.
    return random.Random(10_000 + modem_id)


def _next_rates(modem_id: int, prev_up: int, prev_down: int) -> tuple[int, int]:
    """
    Compute next up/down bps using a mean-reverting random walk.
    """
    rng = _rng_for_modem(modem_id)

    # Derive a "phase" from current second to avoid perfectly static randomness.
    now = int(dt.datetime.now(dt.timezone.utc).timestamp())
    rng.seed(10_000 + modem_id + (now // settings.SAMPLE_INTERVAL_SECONDS))

    # Typical cable modem ranges (roughly), purely simulated.
    up_target = rng.randint(5_000_000, 35_000_000)      # 5-35 Mbps
    down_target = rng.randint(25_000_000, 400_000_000)  # 25-400 Mbps

    def step(prev: int, target: int) -> int:
        # Move 30% toward target, plus noise.
        noise = rng.randint(-2_000_000, 2_000_000)
        nxt = int(prev + 0.30 * (target - prev) + noise)
        return max(0, nxt)

    # If first sample, start near target.
    if prev_up <= 0:
        prev_up = int(up_target * 0.7)
    if prev_down <= 0:
        prev_down = int(down_target * 0.7)

    return step(prev_up, up_target), step(prev_down, down_target)


async def _fetch_modems(session: AsyncSession) -> list[Modem]:
    res = await session.execute(select(Modem).order_by(Modem.id.asc()))
    return list(res.scalars().all())


async def _get_last_sample(session: AsyncSession, modem_id: int) -> TrafficSample | None:
    res = await session.execute(
        select(TrafficSample)
        .where(TrafficSample.modem_id == modem_id)
        .order_by(TrafficSample.timestamp.desc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def _sampling_loop() -> None:
    sessionmaker = get_sessionmaker()

    while not _state.stop_event.is_set():
        started = dt.datetime.now(dt.timezone.utc)
        try:
            async with sessionmaker() as session:
                modems = await _fetch_modems(session)
                for modem in modems:
                    last = await _get_last_sample(session, modem.id)
                    prev_up = last.up_bps if last else 0
                    prev_down = last.down_bps if last else 0
                    up, down = _next_rates(modem.id, prev_up, prev_down)

                    # Timestamp normalized to UTC "now".
                    ts = dt.datetime.now(dt.timezone.utc)
                    session.add(
                        TrafficSample(
                            modem_id=modem.id,
                            timestamp=ts,
                            up_bps=up,
                            down_bps=down,
                        )
                    )
                await session.commit()
        except Exception:
            # Avoid crashing the app due to sampling failures.
            # In production we would log this.
            pass

        elapsed = (dt.datetime.now(dt.timezone.utc) - started).total_seconds()
        sleep_for = max(0.1, settings.SAMPLE_INTERVAL_SECONDS - elapsed)
        try:
            await asyncio.wait_for(_state.stop_event.wait(), timeout=sleep_for)
        except asyncio.TimeoutError:
            continue


# PUBLIC_INTERFACE
async def start_sampler() -> None:
    """Start the background sampler task if not already running."""
    if _state.task is not None and not _state.task.done():
        return
    _state.stop_event.clear()
    _state.task = asyncio.create_task(_sampling_loop(), name="traffic-sampler")


# PUBLIC_INTERFACE
async def stop_sampler() -> None:
    """Stop the background sampler task."""
    _state.stop_event.set()
    if _state.task is not None:
        try:
            await asyncio.wait_for(_state.task, timeout=5)
        except Exception:
            pass
        _state.task = None
