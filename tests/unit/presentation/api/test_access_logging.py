from unittest.mock import MagicMock

import pytest

from src.presentation.api.access_log import build_access_log_event


class TestBuildAccessLogEvent:
    def test_build_access_log_event_with_authenticated_user(self) -> None:
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/users/profile"
        request.url.query = "verbose=1"
        request.user = 123

        event = build_access_log_event(
            request=request,
            status_code=200,
            duration_ms=12.5,
        )

        assert event == {
            "event": "http_request_completed",
            "message": "HTTP request completed",
            "method": "GET",
            "path": "/users/profile",
            "query_string": "verbose=1",
            "status_code": 200,
            "duration_ms": 12.5,
            "user_id": 123,
        }

    def test_build_access_log_event_without_user_or_query_string(self) -> None:
        request = MagicMock()
        request.method = "POST"
        request.url.path = "/auth"
        request.url.query = ""
        request.user = None

        event = build_access_log_event(
            request=request,
            status_code=201,
            duration_ms=3.0,
        )

        assert event == {
            "event": "http_request_completed",
            "message": "HTTP request completed",
            "method": "POST",
            "path": "/auth",
            "query_string": "",
            "status_code": 201,
            "duration_ms": 3.0,
        }

    @pytest.mark.parametrize("invalid_user", [None, "anonymous"])
    def test_build_access_log_event_omits_non_integer_user_id(
        self, invalid_user: object
    ) -> None:
        request = MagicMock()
        request.method = "GET"
        request.url.path = "/health"
        request.url.query = "check=1"
        request.user = invalid_user

        event = build_access_log_event(
            request=request,
            status_code=200,
            duration_ms=1.2,
        )

        assert "user_id" not in event
