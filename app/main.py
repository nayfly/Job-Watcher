# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.core.config import settings
from app.core.logging import configure_logging, RequestIdMiddleware
from app.core import metrics
from app.api.routers import sources, watchlists, alerts, health
from app.db import init_db

configure_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION, lifespan=lifespan)
app.add_middleware(RequestIdMiddleware)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    response = await call_next(request)
    metrics.request_count.labels(request.method, request.url.path, response.status_code).inc()
    return response


app.include_router(sources.router, prefix="/sources", tags=["sources"])
app.include_router(watchlists.router, prefix="/watchlists", tags=["watchlists"])
app.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
app.include_router(health.router, prefix="/health", tags=["health"])


@app.get("/metrics")
def metrics_endpoint():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)