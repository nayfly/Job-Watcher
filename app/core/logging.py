import logging
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

request_id_ctx_var: ContextVar[str | None] = ContextVar("request_id", default=None)


class RequestIdFilter(logging.Filter):
    """Attach the current request_id value to every log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx_var.get() or "-"
        return True


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request id to each incoming request for structured logs."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or request.headers.get("x-request-id")
        if not request_id:
            request_id = str(uuid.uuid4())

        request.state.request_id = request_id
        token = request_id_ctx_var.set(request_id)

        try:
            response = await call_next(request)
        finally:
            request_id_ctx_var.reset(token)

        response.headers["X-Request-ID"] = request_id
        return response


def configure_logging() -> None:
    """Configure Python's logging subsystem for structured output."""

    fmt = "%(asctime)s %(levelname)s %(name)s %(message)s [request_id=%(request_id)s]"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt))
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)

    # optionally, filter out overly verbose libs
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
