import json
import logging
import time
from uuid import UUID, uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger("fixture2030.request")


def build_request_id(value: str | None) -> str:
    if value:
        try:
            return str(UUID(value))
        except ValueError:
            pass

    return str(uuid4())


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = build_request_id(
            request.headers.get("X-Request-ID")
        )

        request.state.request_id = request_id
        request.state.dependency = "api"

        started = time.perf_counter()

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception:
            status_code = 500
            self._write_log(
                request=request,
                status_code=status_code,
                duration_ms=(
                    time.perf_counter() - started
                ) * 1000,
            )
            raise

        duration_ms = (
            time.perf_counter() - started
        ) * 1000

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = (
            f"{duration_ms:.2f}"
        )

        self._write_log(
            request=request,
            status_code=status_code,
            duration_ms=duration_ms,
        )

        return response

    @staticmethod
    def _write_log(
        request: Request,
        status_code: int,
        duration_ms: float,
    ) -> None:
        event = {
            "evento": "http_request",
            "request_id": request.state.request_id,
            "metodo": request.method,
            "ruta": request.url.path,
            "dependencia": getattr(
                request.state,
                "dependency",
                "api",
            ),
            "resultado": status_code,
            "duracion_ms": round(duration_ms, 2),
        }

        logger.info(
            json.dumps(
                event,
                ensure_ascii=False,
            )
        )