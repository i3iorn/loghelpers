# loghelpers/formatters.py
import logging

from . import Configuration
from .context import gather_context
from .utils import BatchForegroundColors, BatchBackgroundColors, redact


class JsonFormatter(logging.Formatter):
    """Formats LogRecord into a JSON string."""
    def __init__(self, config: Configuration):
        super().__init__(
            fmt=config.log_format,
            datefmt=config.date_format
        )
        self.config = config

    def format(self, record: logging.LogRecord) -> str:
        import json
        payload = {
            "timestamp": self.formatTime(record, self.datefmt),
            "logger": record.name,
            "level": record.levelname,
            "message": record.getMessage(),
        }
        payload.update(
            gather_context()
        )
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(redact(payload))

class ColorFormatter(logging.Formatter):
    """Adds ANSI color codes based on level."""
    COLORS = {
        logging.DEBUG: BatchForegroundColors.BLUE,
        logging.INFO: BatchForegroundColors.WHITE,
        logging.WARNING: BatchForegroundColors.YELLOW,
        logging.ERROR: BatchForegroundColors.RED,
        logging.CRITICAL: BatchBackgroundColors.RED,
    }
    RESET = BatchForegroundColors.GREY

    def format(self, record: logging.LogRecord) -> str:
        prefix = self.COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{prefix}{message}{self.RESET}"
