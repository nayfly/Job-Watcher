import logging
import sys

from starlette.requests import Request
from starlette.middleware.base import BaseHTTPMiddleware


class RequestIdFilter(logging.Filter):
    """Attach a default request_id value to all log records."""

    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Attach a request id to each incoming request for structured logs."""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or request.headers.get("x-request-id")
        if not request_id:
            import uuid

            request_id = str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


def configure_logging() -> None:
    """Configure Python's logging subsystem for structured output."""

    fmt = (
        "%(asctime)s %(levelname)s %(name)s %(message)s" " [request_id=%(request_id)s]"
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))

    root = logging.getLogger()
    # add filter to ensure request_id is always present
    root.addFilter(RequestIdFilter())
    root.handlers = [handler]
    root.setLevel(logging.INFO)

    # optionally, filter out overly verbose libs
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
