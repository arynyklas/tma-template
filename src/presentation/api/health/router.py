from litestar import Router, get

from src.infrastructure.logging import get_logger
from src.presentation.api.security import PUBLIC_ROUTE

from .schemas import (
    HealthCheckResponse,
    HealthCheckResponseSchema,
)

logger = get_logger(__name__)


@get("/", return_dto=HealthCheckResponseSchema, **PUBLIC_ROUTE)
async def health_check_handler() -> HealthCheckResponse:
    """Health check endpoint to verify that the application is running."""

    return HealthCheckResponse()


health_router = Router(
    path="/health",
    route_handlers=[health_check_handler],
    tags=["health"],
)
