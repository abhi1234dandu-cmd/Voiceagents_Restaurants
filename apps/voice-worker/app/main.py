from fastapi import FastAPI, WebSocket

from app.config import get_settings
from app.stream import concurrency_stats, handle_media_stream

settings = get_settings()

if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment, traces_sample_rate=0.2)

app = FastAPI(title="Restaurant Voice Worker", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "voice-worker", **concurrency_stats()}


@app.get("/metrics")
def metrics():
    """Autoscaling signal endpoint for Railway / external autoscalers."""
    stats = concurrency_stats()
    return {
        **stats,
        "concurrency_hint": settings.worker_concurrency_hint,
        "utilization": stats["active_streams"] / max(1, settings.worker_concurrency_hint),
    }


@app.websocket("/media")
async def media(websocket: WebSocket):
    await handle_media_stream(websocket, settings)
