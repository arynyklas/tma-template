from dishka.integrations.litestar import setup_dishka
from litestar import Litestar
from litestar.contrib.opentelemetry import OpenTelemetryConfig, OpenTelemetryPlugin
from litestar.exceptions import ClientException, NotAuthorizedException
from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.prometheus import PrometheusConfig
from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.application.auth.exceptions import InvalidInitDataError
from src.application.common.exceptions import ApplicationError, ValidationError
from src.application.interfaces.auth import AuthService
from src.infrastructure.auth import AuthServiceImpl
from src.infrastructure.config import Config
from src.infrastructure.di import AuthProvider, DBProvider, bootstrap_service

from .access_log import AccessLogMiddleware
from .exception import (
    application_error_handler,
    custom_exception_handler,
    exception_logs_handler,
    litestar_error_handler,
    validation_error_handler,
    value_error_handler,
)
from .security import create_jwt_auth
from .utils import setup_routes


def _get_otel_config(config: Config) -> OpenTelemetryConfig:
    resource = Resource.create(
        {
            SERVICE_NAME: "tma-template-api",
        }
    )

    alloy_base = str(config.telemetry.alloy_base.get_secret_value()).removesuffix("/")

    tracer_provider = TracerProvider(resource=resource)
    if config.telemetry.export_traces:
        tracer_provider.add_span_processor(
            BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{alloy_base}/v1/traces"))
        )
    trace.set_tracer_provider(tracer_provider)

    metric_readers = []
    if config.telemetry.export_metrics:
        metric_readers.append(
            PeriodicExportingMetricReader(
                OTLPMetricExporter(endpoint=f"{alloy_base}/v1/metrics")
            )
        )
    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=metric_readers,
    )
    metrics.set_meter_provider(meter_provider)

    otel_config = OpenTelemetryConfig(
        tracer_provider=tracer_provider,
        meter_provider=meter_provider,
    )

    return otel_config


def prepare_app(config: Config) -> Litestar:
    routes = setup_routes()
    jwt_auth = create_jwt_auth(config)

    otel_config = _get_otel_config(config)
    prometheus_config = PrometheusConfig(group_path=False)

    return Litestar(
        route_handlers=[routes],
        plugins=[
            OpenTelemetryPlugin(otel_config),
        ],
        logging_config=None,  # logging is configured separately, via structlog
        middleware=[
            AccessLogMiddleware(),
            prometheus_config.middleware,
        ],
        on_app_init=[jwt_auth.on_app_init],
        openapi_config=OpenAPIConfig(
            title="TMA API",
            description="API for TMA",
            version="0.1.0",
            render_plugins=[ScalarRenderPlugin()],
            path="/schema",
        ),
        exception_handlers={  # type: ignore[invalid-argument-type]
            Exception: custom_exception_handler,
            NotAuthorizedException: litestar_error_handler,
            ClientException: litestar_error_handler,
            ApplicationError: application_error_handler,
            ValidationError: validation_error_handler,
            ValueError: value_error_handler,
            TypeError: value_error_handler,
            InvalidInitDataError: exception_logs_handler,
        },
    )


def create_app() -> Litestar:
    bootstrap = bootstrap_service(
        "tma-template-api",
        AuthProvider(),
        DBProvider(),
        context_builder=lambda config: {
            AuthService: AuthServiceImpl(config),
        },
    )

    app = prepare_app(bootstrap.config)
    setup_dishka(container=bootstrap.container, app=app)

    return app
