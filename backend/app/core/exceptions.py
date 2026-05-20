"""Application-level exceptions and FastAPI exception handlers."""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger


class AiKhbarError(Exception):
    """Base class for all expected application errors."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal error"

    def __init__(self, detail: str | None = None) -> None:
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class NotFoundError(AiKhbarError):
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"


class ExternalServiceError(AiKhbarError):
    """Raised when an upstream dependency (NVIDIA, TTS, scrape target) fails."""

    status_code = status.HTTP_502_BAD_GATEWAY
    detail = "Upstream service error"


class ConfigurationError(AiKhbarError):
    """Raised when required configuration (e.g. an API key) is missing."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service not configured"


class ValidationError(AiKhbarError):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    detail = "Invalid request"


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers that turn AiKhbarError into clean JSON responses."""

    @app.exception_handler(AiKhbarError)
    async def _handle(_: Request, exc: AiKhbarError) -> JSONResponse:
        if exc.status_code >= 500:
            logger.error("AiKhbarError [{}]: {}", exc.status_code, exc.detail)
        else:
            logger.warning("AiKhbarError [{}]: {}", exc.status_code, exc.detail)
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.__class__.__name__, "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(_: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception: {}", exc)
        return JSONResponse(
            status_code=500,
            content={"error": "InternalServerError", "detail": "An unexpected error occurred"},
        )
