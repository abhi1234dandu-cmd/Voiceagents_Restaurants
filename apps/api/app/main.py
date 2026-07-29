from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import (
    admin,
    analytics,
    billing,
    calls,
    jobs,
    orgs,
    pos,
    reservations,
    resources,
    restaurants,
    tools,
    twilio_webhooks,
)
from app.services.seed_demo import seed_demo_if_needed

settings = get_settings()

if settings.sentry_dsn:
    import sentry_sdk

    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment, traces_sample_rate=0.1)

seed_demo_if_needed()

app = FastAPI(title="Restaurant Voice SaaS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.app_url, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orgs.router)
app.include_router(restaurants.router)
app.include_router(resources.router)
app.include_router(reservations.router)
app.include_router(calls.router)
app.include_router(billing.router)
app.include_router(analytics.router)
app.include_router(admin.router)
app.include_router(tools.router)
app.include_router(twilio_webhooks.router)
app.include_router(jobs.router)
app.include_router(pos.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "api", "environment": settings.environment}


@app.get("/openapi-export.json", include_in_schema=False)
def openapi_export():
    return app.openapi()
