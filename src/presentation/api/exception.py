import logging
from typing import Any

from litestar import Request, Response

logger = logging.getLogger(__name__)


def custom_exception_handler(_: Request[Any, Any, Any], exc: Exception) -> Response[Any]:
    logger.exception(exc)
    return Response({"detail": "Internal Server Error", "status_code": 500}, status_code=500)
