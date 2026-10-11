import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

from app.exceptions import ApiError


logger = logging.getLogger("fixture2030.error")


def get_request_id(request: Request) -> str:
    return getattr(
        request.state,
        "request_id",
        "request-id-no-disponible",
    )


def build_error_response(
    request: Request,
    status_code: int,
    code: str,
    message: str,
    details: Any | None = None,
) -> JSONResponse:
    request_id = get_request_id(request)

    error = {
        "codigo": code,
        "mensaje": message,
        "request_id": request_id,
    }

    if details is not None:
        error["detalles"] = details

    return JSONResponse(
        status_code=status_code,
        content={"error": error},
        headers={"X-Request-ID": request_id},
    )


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def api_error_handler(
        request: Request,
        error: ApiError,
    ) -> JSONResponse:
        if error.dependency:
            request.state.dependency = error.dependency

        logger.warning(
            "request_id=%s codigo=%s status=%s",
            get_request_id(request),
            error.code,
            error.status_code,
        )

        return build_error_response(
            request=request,
            status_code=error.status_code,
            code=error.code,
            message=error.message,
            details=error.details,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request,
        error: RequestValidationError,
    ) -> JSONResponse:
        details = [
            {
                "campo": ".".join(
                    str(part)
                    for part in item["loc"]
                ),
                "mensaje": item["msg"],
                "tipo": item["type"],
            }
            for item in error.errors()
        ]

        return build_error_response(
            request=request,
            status_code=422,
            code="DATOS_INVALIDOS",
            message=(
                "Los datos enviados no superaron "
                "la validación."
            ),
            details=details,
        )

    @app.exception_handler(HTTPException)
    async def http_error_handler(
        request: Request,
        error: HTTPException,
    ) -> JSONResponse:
        return build_error_response(
            request=request,
            status_code=error.status_code,
            code=f"HTTP_{error.status_code}",
            message=str(error.detail),
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(
        request: Request,
        error: Exception,
    ) -> JSONResponse:
        logger.exception(
            "request_id=%s error_inesperado=%s",
            get_request_id(request),
            type(error).__name__,
        )

        return build_error_response(
            request=request,
            status_code=500,
            code="ERROR_INTERNO",
            message=(
                "Ocurrió un error interno inesperado."
            ),
        )