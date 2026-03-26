import os

from litestar import Router, get
from litestar.response import Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    REGISTRY,
    CollectorRegistry,
    generate_latest,
    multiprocess,
)
from prometheus_client.openmetrics.exposition import (
    CONTENT_TYPE_LATEST as OPENMETRICS_CONTENT_TYPE_LATEST,
)
from prometheus_client.openmetrics.exposition import (
    generate_latest as openmetrics_generate_latest,
)

from src.presentation.api.security import ACCESS_SECURED_ROUTE

from .guards import metrics_auth_guard

__all__ = ("metrics_router",)

OPENMETRICS_FORMAT = False


@get(
    "/",
    **ACCESS_SECURED_ROUTE,
    guards=[metrics_auth_guard],
    description="Expose Prometheus metrics for authenticated scraping.",
)
async def get_metrics_handler() -> Response:
    # adapted from litestar.plugins.prometheus.controller.PrometheusController
    registry = REGISTRY
    if (
        "prometheus_multiproc_dir" in os.environ
        or "PROMETHEUS_MULTIPROC_DIR" in os.environ
    ):
        registry = CollectorRegistry()
        multiprocess.MultiProcessCollector(registry)

    if OPENMETRICS_FORMAT:
        headers = {"Content-Type": OPENMETRICS_CONTENT_TYPE_LATEST}
        return Response(
            openmetrics_generate_latest(registry), status_code=200, headers=headers
        )

    headers = {"Content-Type": CONTENT_TYPE_LATEST}
    return Response(generate_latest(registry), status_code=200, headers=headers)


metrics_router = Router(
    path="/metrics",
    route_handlers=[get_metrics_handler],
    tags=["metrics"],
)
