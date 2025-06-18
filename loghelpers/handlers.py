import logging
import os
from logging import Handler, StreamHandler
from logging.handlers import RotatingFileHandler
from typing import Optional

from .config import Configuration
from .formatters import ColorFormatter, JsonFormatter
from .utils import get_root_path


def create_console_handler(config: Configuration) -> Handler:
    """
    Create and configure a console log handler.

    Args:
        config (Configuration): Configuration object with log level and format settings.

    Returns:
        Handler: Configured StreamHandler with ColorFormatter.
    """
    handler = StreamHandler()
    handler.setLevel(config.log_level)
    handler.setFormatter(ColorFormatter(fmt="[{levelname}] {message}", style="{"))
    return handler


def create_file_handler(config: Configuration) -> Handler:
    """
    Create and configure a file log handler with rotation support and JSON formatting.

    Args:
        config (Configuration): Configuration object with log file path and log level.

    Returns:
        Handler: Configured FileHandler or RotatingFileHandler with JsonFormatter.
    """
    log_path = config.log_file or os.path.join(get_root_path(), "app.log")
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    handler: Handler = RotatingFileHandler(
        filename=log_path,
        mode="a",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=3,
        encoding="utf-8",
        delay=True,
    )
    handler.setLevel(config.log_level)
    handler.setFormatter(JsonFormatter(config))
    return handler


def create_json_file_handler(
    path: Optional[str] = None,
    level: Optional[str] = "INFO",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
) -> Handler:
    """
    Create a standalone JSON-formatted file handler, optionally outside the Configuration object.

    Args:
        path (Optional[str]): Path to the log file.
        level (Optional[str]): Logging level as a string.
        max_bytes (int): Max file size before rotation.
        backup_count (int): Number of rotated logs to retain.

    Returns:
        Handler: Configured RotatingFileHandler with JSON output.
    """
    path = path or os.path.join(get_root_path(), "json.log")
    os.makedirs(os.path.dirname(path), exist_ok=True)

    handler = RotatingFileHandler(
        filename=path,
        mode="a",
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
        delay=True,
    )
    handler.setLevel(getattr(logging, level.upper(), logging.INFO))
    handler.setFormatter(JsonFormatter())
    return handler
