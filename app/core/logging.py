import logging
import sys
import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response


LOG_FORMAT = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
REQUEST_ID_HEADER = "X-Request-ID"


def configure_logging() -> None:
    logger = logging.getLogger("resume")
    if logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(f"resume.{name}")


async def log_requests(request: Request, call_next: Callable[[Request], Response]) -> Response:
    logger = get_logger("http")
    request_id = request.headers.get(REQUEST_ID_HEADER) or uuid.uuid4().hex[:12]
    request.state.request_id = request_id

    forwarded_for = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    client_ip = forwarded_for or (request.client.host if request.client else "unknown")
    started_at = time.perf_counter()

    logger.info(
        "request_started request_id=%s method=%s path=%s client_ip=%s",
        request_id,
        request.method,
        request.url.path,
        client_ip,
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
        logger.exception(
            "request_failed request_id=%s method=%s path=%s duration_ms=%s",
            request_id,
            request.method,
            request.url.path,
            duration_ms,
        )
        raise

    duration_ms = round((time.perf_counter() - started_at) * 1000, 2)
    response.headers[REQUEST_ID_HEADER] = request_id
    logger.info(
        "request_finished request_id=%s method=%s path=%s status_code=%s duration_ms=%s",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response
