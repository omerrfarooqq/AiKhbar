"""Centralised logging configuration using loguru.

Call `configure_logging()` once at startup. Everywhere else just do
`from loguru import logger` and use it directly.
"""
import logging
import sys

from loguru import logger

from app.core.config import settings


class _InterceptHandler(logging.Handler):
    """Route stdlib logging (uvicorn, sqlalchemy, apscheduler) through loguru."""

    def emit(self, record: logging.LogRecord) -> None:  # noqa: D102
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        frame, depth = logging.currentframe(), 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1
        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


def configure_logging() -> None:
    """Initialise logging sinks and intercept stdlib loggers."""
    logger.remove()

    if settings.log_json:
        logger.add(sys.stdout, level=settings.log_level, serialize=True)
    else:
        logger.add(
            sys.stdout,
            level=settings.log_level,
            colorize=True,
            format=(
                "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                "<level>{level: <8}</level> | "
                "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>"
            ),
        )

    logger.add(
        "logs/aikhbar_{time:YYYY-MM-DD}.log",
        rotation="00:00",
        retention="14 days",
        level=settings.log_level,
        enqueue=True,
    )

    logging.basicConfig(handlers=[_InterceptHandler()], level=0, force=True)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "sqlalchemy.engine",
                 "apscheduler"):
        logging.getLogger(name).handlers = [_InterceptHandler()]
        logging.getLogger(name).propagate = False

    logger.info("Logging configured | level={} | env={}", settings.log_level,
                settings.app_env)
