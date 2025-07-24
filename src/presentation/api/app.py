from litestar import Litestar

from .health.router import health_router


def create_app() -> Litestar:
    return Litestar(
        route_handlers=[
            health_router,
        ],
    )
