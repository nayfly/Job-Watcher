from fastapi import FastAPI, Request, Response

from app.core.config import settings
from app.core.logging import configure_logging, RequestIdMiddleware
from app.core import metrics
from app.api.routers import sources, watchlists, alerts, health
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST


# configure logging before anything else
configure_logging()

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.add_middleware(RequestIdMiddleware)


@app.on_event("startup")
def on_startup():
    # create tables if they don't exist (sqlite/dev convenience)
    from app.db import init_db

    init_db()


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    # increment basic request counter
    metrics.request_count.labels(
        request.method, request.url.path, response.status_code
    ).inc()
    return response


# router registration
app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(health.router, prefix="/health", tags=["health"])


# expose prometheus metrics as a simple path
@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
