# Traffic Backend (Cable Modem Traffic Monitor)

FastAPI backend that:
- Stores modems and time-series traffic samples
- Simulates traffic sampling in the background
- Serves historical aggregated stats
- Streams realtime upload/download rates via WebSocket

## Running locally

From this folder:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 3001 --reload
```

Then open:
- Swagger UI: http://localhost:3001/docs
- OpenAPI JSON: http://localhost:3001/openapi.json

## Configuration

Environment variables (optional):
- `DB_URL` (default: `sqlite+aiosqlite:///./traffic.db`)
- `CORS_ORIGIN` (default: `http://localhost:3000`)
- `SAMPLE_INTERVAL_SECONDS` (default: `5`)
- `REALTIME_EMIT_SECONDS` (default: `1`)

## Database

Tables:
- `modems`: `id, name, ip, status, created_at`
- `traffic_samples`: `id, modem_id, timestamp, up_bps, down_bps`

On startup, if no modems exist, a seed modem is created:
- name: `Default Modem`
- ip: `192.168.100.1`

## API Endpoints

### Health
- `GET /` → `{ "message": "Healthy" }`

### Modems CRUD
- `POST /modems`
- `GET /modems`
- `GET /modems/{id}`
- `PUT /modems/{id}`
- `DELETE /modems/{id}`

### Historical stats
- `GET /modems/{id}/stats?from=ISO8601&to=ISO8601&granularity=1m|5m|1h`

Returns aggregated (average) bps per bucket.

Example:

```
GET /modems/1/stats?from=2026-01-02T00:00:00Z&to=2026-01-02T01:00:00Z&granularity=1m
```

### Realtime stream (WebSocket)
- `WS /modems/{id}/realtime`

Emits about once per second:

```json
{"timestamp":"2026-01-02T00:00:00+00:00","up_bps":123,"down_bps":456}
```

## Notes

This backend simulates traffic; it does not query real modem devices yet. The sampling/service layer is structured so real ingestion can be swapped in later.
