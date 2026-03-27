import hashlib
import logging
from pathlib import Path
import tempfile

import certifi
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

from src.infrastructure.config import TelemetryConfig


def build_sentry_logging_integration() -> LoggingIntegration:
    return LoggingIntegration(
        level=None,
        event_level=logging.ERROR,
        sentry_logs_level=logging.INFO,
    )


def _build_sentry_ca_bundle(custom_ca_certs: str | None) -> str | None:
    default_bundle = Path(certifi.where())
    merged_bundle_contents = default_bundle.read_text(encoding="utf-8")
    if custom_ca_certs:
        merged_bundle_contents += Path(custom_ca_certs).read_text(encoding="utf-8")

    merged_bundle_hash = hashlib.sha256(
        merged_bundle_contents.encode("utf-8")
    ).hexdigest()
    merged_bundle_path = (
        Path(tempfile.gettempdir()) / f"sentry-ca-bundle-{merged_bundle_hash}.pem"
    )

    if not merged_bundle_path.exists():
        merged_bundle_path.write_text(merged_bundle_contents, encoding="utf-8")

    return str(merged_bundle_path)


def init_sentry(config: TelemetryConfig, *, service_name: str) -> None:
    if config.sentry_dsn is None:
        return

    sentry_sdk.init(
        dsn=str(config.sentry_dsn),
        traces_sample_rate=config.sentry_traces_sample_rate,
        ca_certs=_build_sentry_ca_bundle(config.sentry_ca_certs),
        include_local_variables=True,
        server_name=service_name,
        enable_logs=True,
        integrations=[build_sentry_logging_integration()],
    )
