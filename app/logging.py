import sys
import json
import logging
from types import FrameType
from typing import cast, Any, Dict, TYPE_CHECKING

from loguru import logger

if TYPE_CHECKING:
    import loguru


class InterceptHandler(logging.Handler):
    """
    Intercepts standard logging and redirects to loguru.
    This enables loguru to handle logs from libraries using standard logging.
    """

    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from frame
        frame, depth = sys._getframe(6), 6
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = cast(FrameType, frame.f_back)
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


class JsonSink:
    """
    Custom sink for loguru that formats logs as JSON.
    """

    def __call__(self, message: "loguru.Message") -> None:
        record = message.record
        log_data: Dict[str, Any] = {
            "timestamp": record["time"].isoformat(),
            "level": record["level"].name,
            "message": record["message"],
            "module": record["name"],
        }

        # Include exception info if available
        if record["exception"]:
            log_data["exception"] = str(record["exception"])
            # Safely access traceback if it exists
            if hasattr(record["exception"], "traceback"):
                log_data["traceback"] = str(record["exception"].traceback)

        # Include extra fields
        if record["extra"]:
            log_data["extra"] = record["extra"]

        # Print as JSON
        print(json.dumps(log_data), file=sys.stdout)


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure logging with loguru.
    Uses JSON formatting in production environments.

    Args:
        log_level: The minimum log level to capture
    """
    # Remove default handler
    logger.remove()

    # Configure JSON handler
    logger.configure(handlers=[{"sink": JsonSink(), "level": log_level.upper()}])

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Set third-party loggers to specified level
    for logger_name in ("uvicorn", "uvicorn.error", "fastapi"):
        logging.getLogger(logger_name).setLevel(log_level.upper())

    logger.info(f"Logging initialized at {log_level} level")
