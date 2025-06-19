# loghelpers/formatters.py
import logging

import orjson

from .config import Configuration
from .context import LoggingContext
from .utils import BatchForegroundColors, BatchBackgroundColors


class JsonFormatter(logging.Formatter):
    """Formats LogRecord into a JSON string."""
    def __init__(self, config: Configuration):
        super().__init__(
            fmt=config.log_format,
            datefmt=config.date_format
        )
        self.config = config
        self.context = LoggingContext()

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        payload.update(
            self.context.resolve_context(self.config)
        )
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return orjson.dumps(self.config.redactor.redact(payload)).decode()


class ColorFormatter(logging.Formatter):
    """Adds ANSI color codes based on level."""
    COLORS = {
        logging.DEBUG: BatchForegroundColors.BLUE.value,
        logging.INFO: BatchForegroundColors.WHITE.value,
        logging.WARNING: BatchForegroundColors.YELLOW.value,
        logging.ERROR: BatchForegroundColors.RED.value,
        logging.CRITICAL: BatchBackgroundColors.RED.value,
    }
    RESET = BatchForegroundColors.GREY.value

    def format(self, record: logging.LogRecord) -> str:
        prefix = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{prefix}{message}{self.RESET}"

