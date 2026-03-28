from http import HTTPStatus
from unittest.mock import Mock

from litestar import Request

from src.application.common.exceptions import ApplicationError
from src.presentation.api.exception import (
    application_error_handler,
    custom_exception_handler,
)


class ConflictError(ApplicationError):
    status_code = HTTPStatus.CONFLICT


def _make_request(*, method: str, path: str, query_string: str = "") -> Request:
    async def receive() -> dict[str, object]:
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(_message: dict[str, object]) -> None:
        return None

    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": method,
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "query_string": query_string.encode(),
        "root_path": "",
        "headers": [],
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
        "app": None,
        "route_handler": None,
        "state": {},
    }
    return Request(scope=scope, receive=receive, send=send)


def test_custom_exception_handler_logs_request_context(monkeypatch) -> None:
    logger = Mock()
    request = _make_request(method="GET", path="/users/me", query_string="active=true")
    exc = RuntimeError("boom")

    monkeypatch.setattr("src.presentation.api.exception.logger", logger)

    response = custom_exception_handler(request, exc)

    logger.exception.assert_called_once()
    kwargs = logger.exception.call_args.kwargs
    assert kwargs["event"] == "internal_server_error"
    assert kwargs["request_method"] == "GET"
    assert kwargs["request_path"] == "/users/me"
    assert kwargs["request_query"] == "active=true"
    assert response.status_code == HTTPStatus.INTERNAL_SERVER_ERROR


def test_application_error_handler_logs_request_context(monkeypatch) -> None:
    logger = Mock()
    request = _make_request(method="POST", path="/users", query_string="")
    exc = ConflictError("Invalid state")

    monkeypatch.setattr("src.presentation.api.exception.logger", logger)

    response = application_error_handler(request, exc)

    logger.exception.assert_called_once()
    kwargs = logger.exception.call_args.kwargs
    assert kwargs["event"] == "application_error"
    assert kwargs["request_method"] == "POST"
    assert kwargs["request_path"] == "/users"
    assert kwargs["request_query"] == ""
    assert kwargs["error_message"] == "Invalid state"
    assert response.status_code == HTTPStatus.CONFLICT
