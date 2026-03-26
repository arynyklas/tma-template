from dishka.integrations.litestar import FromDishka, inject_asgi
from litestar.connection import ASGIConnection
from litestar.handlers import BaseRouteHandler

from src.infrastructure.config import Config
from src.presentation.api.security import require_secret


@inject_asgi
async def metrics_auth_guard(
    connection: ASGIConnection,
    _: BaseRouteHandler,
    config: FromDishka[Config],
) -> None:
    require_secret(connection, config.metrics.secret)
