from __future__ import annotations

import textwrap

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.routers.modems import router as modems_router
from src.api.routers.traffic import router as traffic_router
from src.services.db_init import init_db
from src.services.sampling import start_sampler, stop_sampler
from src.settings import settings

openapi_tags = [
    {"name": "System", "description": "Health and service information."},
    {"name": "Modems", "description": "CRUD operations for monitored modems."},
    {"name": "Traffic", "description": "Historical stats and realtime streaming."},
]

app = FastAPI(
    title="Cable Modem Traffic Monitor API",
    description="Backend service to register modems, collect simulated traffic samples, and serve historical + realtime stats.",
    version="0.1.0",
    openapi_tags=openapi_tags,
)

# CORS: allow the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(modems_router)
app.include_router(traffic_router)


@app.on_event("startup")
async def _startup() -> None:
    """Initialize database, seed defaults, and start sampler background loop."""
    await init_db()
    await start_sampler()


@app.on_event("shutdown")
async def _shutdown() -> None:
    """Stop background sampler."""
    await stop_sampler()


@app.get(
    "/",
    tags=["System"],
    summary="Health check",
    description="Simple health check endpoint.",
    operation_id="health_check",
)
def health_check() -> dict:
    """Return service health status."""
    return {"message": "Healthy"}


@app.get(
    "/docs/realtime",
    tags=["System"],
    summary="Realtime WebSocket usage",
    description="Documentation helper for using the realtime websocket endpoint.",
    operation_id="realtime_usage",
)
def realtime_usage() -> dict:
    """Provide instructions for connecting to the realtime WebSocket endpoint."""
    return {
        "websocket": {
            "endpoint": "/modems/{id}/realtime",
            "message_format": {"timestamp": "ISO8601", "up_bps": 0, "down_bps": 0},
            "notes": "Emits about once per second. Useful for live UI updates.",
        },
        "example_javascript": textwrap.dedent(
            """
            const ws = new WebSocket("ws://localhost:3001/modems/1/realtime");
            ws.onmessage = (evt) => console.log(JSON.parse(evt.data));
            """
        ).strip(),
    }
