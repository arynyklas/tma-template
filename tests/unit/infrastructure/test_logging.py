from io import StringIO
import json
import logging

from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import (
    NonRecordingSpan,
    SpanContext,
    TraceFlags,
    set_span_in_context,
)
import pytest

from src.domain.user.vo import UserId
from src.infrastructure.logging import (
    LOG_JSON_ENV_VAR,
    _renderer,
    add_trace_context,
    configure_logging,
    get_logger,
    is_json_logs_enabled,
)
from src.infrastructure.telemetry.sentry import build_sentry_logging_integration


class TestLoggingConfiguration:
    def test_non_json_renderer_uses_console_renderer(self) -> None:
        renderer = _renderer(json_logs=False)
        rendered = renderer(
            None,
            "info",
            {
                "message": "User logged in",
                "event": "user_logged_in",
                "user_id": 123,
                "level": "info",
                "logger": "tests.logging",
                "timestamp": "2026-03-26T08:32:49.265628Z",
            },
        )

        assert "User logged in" in rendered
        assert "event" in rendered
        assert "user_logged_in" in rendered
        assert "user_id" in rendered
        assert "123" in rendered

    def test_is_json_logs_enabled_false_by_default(
        self, monkeypatch: pytest.MonkeyPatch
    ):
        monkeypatch.delenv(LOG_JSON_ENV_VAR, raising=False)

        assert is_json_logs_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "TRUE", "yes", "on"])
    def test_is_json_logs_enabled_true_values(
        self, monkeypatch: pytest.MonkeyPatch, value: str
    ) -> None:
        monkeypatch.setenv(LOG_JSON_ENV_VAR, value)

        assert is_json_logs_enabled() is True

    def test_configure_logging_emits_json_logs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LOG_JSON_ENV_VAR, "true")
        output = StringIO()
        monkeypatch.setattr("sys.stdout", output)

        configure_logging()

        logger = get_logger("tests.logging")
        logger.info(
            event="user_logged_in",
            message="User logged in",
            user_id=123,
        )

        rendered = output.getvalue().strip()
        payload = json.loads(rendered)
        assert payload["event"] == "user_logged_in"
        assert payload["message"] == "User logged in"
        assert payload["user_id"] == 123
        assert payload["logger"] == "tests.logging"
        assert payload["level"] == "info"
        assert "timestamp" in payload

    def test_configure_logging_serializes_value_objects_in_json_logs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LOG_JSON_ENV_VAR, "true")
        output = StringIO()
        monkeypatch.setattr("sys.stdout", output)

        configure_logging()

        logger = get_logger("tests.logging")
        logger.info(
            event="user_loaded",
            message="User loaded",
            user_id=UserId(123),
        )

        rendered = output.getvalue().strip()
        payload = json.loads(rendered)

        assert payload["user_id"] == 123

    def test_configure_logging_emits_human_readable_logs(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LOG_JSON_ENV_VAR, "false")

        configure_logging()

        rendered = _renderer(json_logs=False)(
            None,
            "info",
            {
                "message": "User logged in",
                "event": "user_logged_in",
                "user_id": 123,
                "level": "info",
                "logger": "tests.logging",
                "timestamp": "2026-03-26T08:32:49.265628Z",
            },
        )

        assert "User logged in" in rendered
        assert "event" in rendered
        assert "user_logged_in" in rendered
        assert "user_id" in rendered
        assert "123" in rendered
        assert "{'event':" not in rendered
        assert "INFO -" not in rendered
        assert "\x1b[" in rendered

    def test_add_trace_context_includes_active_span_ids(self) -> None:
        provider = TracerProvider()
        tracer = provider.get_tracer(__name__)

        with tracer.start_as_current_span("log-test") as span:
            event_dict = add_trace_context(None, "info", {})
            span_context = span.get_span_context()

        assert event_dict["trace_id"] == f"{span_context.trace_id:032x}"
        assert event_dict["span_id"] == f"{span_context.span_id:016x}"

    def test_add_trace_context_ignores_invalid_span(self) -> None:
        span = NonRecordingSpan(
            SpanContext(
                trace_id=0,
                span_id=0,
                is_remote=False,
                trace_flags=TraceFlags(0),
                trace_state={},
            )
        )
        context = set_span_in_context(span)

        event_dict = add_trace_context(None, "info", {}, context)

        assert event_dict == {}

    def test_stdlib_logs_are_rendered_consistently(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LOG_JSON_ENV_VAR, "true")
        output = StringIO()
        monkeypatch.setattr("sys.stdout", output)

        configure_logging()

        logging.getLogger("stdlib.test").info("Plain stdlib message")

        payload = json.loads(output.getvalue().strip())
        assert payload["event"] == "Plain stdlib message"
        assert payload["message"] == "Plain stdlib message"
        assert payload["logger"] == "stdlib.test"
        assert payload["level"] == "info"

    def test_sentry_logging_integration_disables_breadcrumbs(self) -> None:
        integration = build_sentry_logging_integration()

        assert integration._handler.level == logging.ERROR
        assert integration._breadcrumb_handler is None
        assert integration._sentry_logs_handler.level == logging.INFO

    def test_stdlib_exception_logs_reach_console(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv(LOG_JSON_ENV_VAR, "true")
        output = StringIO()
        monkeypatch.setattr("sys.stdout", output)

        configure_logging()

        try:
            raise RuntimeError("boom")
        except RuntimeError:
            logging.getLogger("stdlib.test").exception("Plain stdlib exception")

        payload = json.loads(output.getvalue().strip())
        assert payload["event"] == "Plain stdlib exception"
        assert payload["message"] == "Plain stdlib exception"
        assert payload["logger"] == "stdlib.test"
        assert payload["level"] == "error"
        assert "exception" in payload
