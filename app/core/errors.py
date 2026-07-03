from fastapi import HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


def error_response(
        *,
        status_code: int,
        code: str,
        message: str,
        details: object | None = None,
) -> JSONResponse:
    payload: dict[str, object] = {
        "error": {
            "code": code,
            "message": message,
        },
    }

    if details is not None:
        payload["error"]["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=payload,
    )

async def http_exception_handler(
        request: Request,
        exc: HTTPException,
) -> JSONResponse:
    return error_response(
        status_code=exc.status_code,
        code="http_error",
        message=str(exc.detail),
    )

async def validation_exception_handler(
        request: Request,
        exc: RequestValidationError,
) -> JSONResponse:
    return error_response(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        code="validation_error",
        message="Request validation failed.",
        details=exc.errors(),
    )

async def sqlalchemy_exception_handler(
        request: Request,
        exc: SQLAlchemyError,
) -> JSONResponse:
    return error_response(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        code="database_error",
        message="Database operation failed.",
    )

async def unhandled_exception_handler(
        request: Request,
        exc: Exception,
) -> JSONResponse:
    return error_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        code="internal_server_error",
        message="Unexpected internal server error.",
    )