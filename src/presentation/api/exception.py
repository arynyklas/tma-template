from http import HTTPStatus

from litestar import Request, Response
from litestar.exceptions import ClientException
from pydantic import ValidationError as PydanticValidationError

from src.application.common.exceptions import ApplicationError, ValidationError
from src.infrastructure.logging import get_logger
from src.presentation.api.base.schemas import CamelModel

logger = get_logger(__name__)


class FieldError(CamelModel):
    field: str
    message: str


class ErrorResponse(CamelModel):
    detail: str
    status_code: int


class ValidationErrorResponse(CamelModel):
    detail: str
    status_code: int
    errors: list[FieldError]


def _request_context(request: Request) -> dict[str, str]:
    return {
        "request_method": request.method,
        "request_path": request.url.path,
        "request_query": request.url.query,
    }


def custom_exception_handler(
    request: Request, exc: Exception
) -> Response[ErrorResponse]:
    logger.exception(
        event="internal_server_error",
        message="Internal server error",
        error_type=type(exc).__name__,
        **_request_context(request),
    )

    return Response(
        ErrorResponse(
            detail="Internal Server Error",
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
        ),
        status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
    )


def litestar_error_handler(_: Request, exc: ClientException) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=exc.detail, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def exception_logs_handler(_: Request, exc: ValidationError) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=exc.message, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def validation_error_handler(
    _: Request, exc: ValidationError
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=exc.message, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def application_error_handler(
    request: Request, exc: ApplicationError
) -> Response[ErrorResponse]:
    logger.exception(
        event="application_error",
        message="Application error",
        error_message=exc.message,
        status_code=exc.status_code,
        **_request_context(request),
    )

    return Response(
        ErrorResponse(detail=exc.message, status_code=exc.status_code),
        status_code=exc.status_code,
    )


def pydantic_validation_error_handler(
    _: Request, exc: PydanticValidationError
) -> Response[ValidationErrorResponse]:
    field_errors = [
        FieldError(
            field=" -> ".join(str(loc) for loc in e["loc"]),
            message=e["msg"],
        )
        for e in exc.errors()
    ]
    return Response(
        ValidationErrorResponse(
            detail="Validation error",
            status_code=HTTPStatus.BAD_REQUEST,
            errors=field_errors,
        ),
        status_code=HTTPStatus.BAD_REQUEST,
    )


def value_error_handler(
    _: Request, exc: ValueError | TypeError
) -> Response[ErrorResponse]:
    return Response(
        ErrorResponse(detail=str(exc), status_code=HTTPStatus.BAD_REQUEST),
        status_code=HTTPStatus.BAD_REQUEST,
    )
