from collections.abc import Mapping, MutableMapping
import logging
import os
import sys
from typing import cast

from opentelemetry import context as otel_context
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.trace import SpanContext
import structlog
from structlog.types import EventDict, Processor, WrappedLogger

from src.domain.common.vo.base import BaseValueObject

LOG_JSON_ENV_VAR = "LOG_JSON"
_TRACE_ID_HEX_LENGTH = 32
_SPAN_ID_HEX_LENGTH = 16


def configure_logging(
    service_name: str | None = None,
    *,
    json_logs: bool | None = None,
) -> None:
    shared_processors = _shared_processors()
    renderer = _renderer(is_json_logs_enabled() if json_logs is None else json_logs)
    processor_formatter = structlog.stdlib.ProcessorFormatter(
        processor=renderer,
        foreign_pre_chain=shared_processors,
    )
    console_handler = logging.StreamHandler(stream=sys.stdout)
    console_handler.setFormatter(processor_formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(console_handler)

    structlog.reset_defaults()
    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    return structlog.stdlib.get_logger(name)


def is_json_logs_enabled() -> bool:
    return os.environ.get(LOG_JSON_ENV_VAR, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def add_trace_context(
    _: WrappedLogger,
    __: str,
    event_dict: EventDict,
    context: otel_context.Context | None = None,
) -> EventDict:
    span = trace.get_current_span(context)
    span_context = span.get_span_context()
    if not _is_valid_span_context(span_context):
        return event_dict

    event_dict["trace_id"] = format(span_context.trace_id, f"0{_TRACE_ID_HEX_LENGTH}x")
    event_dict["span_id"] = format(span_context.span_id, f"0{_SPAN_ID_HEX_LENGTH}x")
    return event_dict


def normalize_message(
    _: WrappedLogger, __: str, event_dict: MutableMapping[str, object]
) -> EventDict:
    message = event_dict.pop("message", None)
    event = event_dict.get("event")

    if not isinstance(message, str):
        if isinstance(event, str):
            event_dict["message"] = event
            return cast(EventDict, event_dict)

        msg = "Structured logs require 'message' or string 'event'"
        raise ValueError(msg)

    if not isinstance(event, str):
        msg = "Structured logs require string 'event'"
        raise ValueError(msg)

    event_dict["event"] = event
    event_dict["message"] = message

    return cast(EventDict, _serialize_value_objects(event_dict))


def _serialize_value_objects(
    event_dict: MutableMapping[str, object],
) -> MutableMapping[str, object]:
    for key, value in event_dict.items():
        if isinstance(value, BaseValueObject):
            event_dict[key] = value.value

    return event_dict


def _shared_processors() -> list[Processor]:
    return [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        add_trace_context,
        normalize_message,
        structlog.processors.format_exc_info,
    ]


def _renderer(json_logs: bool) -> Processor:
    if json_logs:
        return cast(Processor, structlog.processors.JSONRenderer())

    return cast(
        Processor,
        structlog.dev.ConsoleRenderer(
            colors=True,
            force_colors=True,
            event_key="message",
        ),
    )


def _build_otlp_log_handler(
    *,
    endpoint: str,
    service_name: str | None,
) -> logging.Handler:
    resource = Resource.create(
        {"service.name": service_name} if service_name is not None else {}
    )

    logger_provider = LoggerProvider(resource)

    set_logger_provider(logger_provider)

    logger_provider.add_log_record_processor(
        BatchLogRecordProcessor(OTLPLogExporter(endpoint=endpoint))
    )

    return LoggingHandler(
        level=logging.NOTSET,
        logger_provider=logger_provider,
    )


def _is_valid_span_context(span_context: SpanContext) -> bool:
    return span_context.is_valid and (
        span_context.trace_id != 0 or span_context.span_id != 0
    )


def build_event_kwargs(
    *,
    event: str,
    message: str,
    **extra: str | int | float,
) -> Mapping[str, str | int | float]:
    return {"event": event, "message": message, **extra}
