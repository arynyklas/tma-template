import logging

import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from src.infrastructure.config import TelemetryConfig


def build_sentry_logging_integration() -> LoggingIntegration:
    return LoggingIntegration(
        level=None,
        event_level=logging.ERROR,
        sentry_logs_level=logging.INFO,
    )


def init_sentry(config: TelemetryConfig, *, service_name: str) -> None:
    if config.sentry_dsn is None:
        return

    sentry_sdk.init(
        dsn=str(config.sentry_dsn),
        environment=config.sentry_environment,
        release=config.sentry_release,
        traces_sample_rate=config.sentry_traces_sample_rate,
        ca_certs=config.sentry_ca_certs,
        include_local_variables=True,
        server_name=service_name,
        enable_logs=True,
        integrations=[build_sentry_logging_integration()],
    )
