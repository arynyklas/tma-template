from time import perf_counter
from typing import Any, cast

from litestar import Request
from litestar.middleware import ASGIMiddleware
from litestar.types import ASGIApp, Message, Receive, Scope, Send

from src.infrastructure.logging import build_event_kwargs, get_logger

logger = get_logger(__name__)


def build_access_log_event(
    *,
    request: Request[Any, Any, Any],
    status_code: int,
    duration_ms: float,
) -> dict[str, str | int | float]:
    event: dict[str, str | int | float] = {
        **build_event_kwargs(
            event="http_request_completed",
            message="HTTP request completed",
        ),
        "method": request.method,
        "path": request.url.path,
        "query_string": request.url.query,
        "status_code": status_code,
        "duration_ms": duration_ms,
    }
    if request.scope.get("user") and isinstance(request.user, int):
        event["user_id"] = request.user

    return event


class AccessLogMiddleware(ASGIMiddleware):
    async def handle(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
        next_app: ASGIApp,
    ) -> None:
        start = perf_counter()
        status_code = 500

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])

            await send(message)

        try:
            await next_app(scope, receive, send_wrapper)

        finally:
            duration_ms = round((perf_counter() - start) * 1000, 3)
            request = Request(scope=scope, receive=receive, send=send)
            event_data = build_access_log_event(
                request=request,
                status_code=status_code,
                duration_ms=duration_ms,
            )
            logger.info(cast(str, event_data.pop("event")), **event_data)
