import importlib
import logging
import os
from logging import Handler, StreamHandler
from logging.handlers import RotatingFileHandler

from .config import Configuration
from .formatters import ColorFormatter, JsonFormatter
from .utils import get_root_path


class SensitiveDataFilter(logging.Filter):
    """
    A logging filter to mask sensitive data in log messages.
    """

    SENSITIVE_KEYS = ["password", "token", "secret"]

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            for key in self.SENSITIVE_KEYS:
                record.msg = record.msg.replace(key, "***")
        return True


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
    handler.addFilter(SensitiveDataFilter())
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
    handler.addFilter(SensitiveDataFilter())
    return handler


def load_handler(handler_name: str, **kwargs) -> logging.Handler:
    """
    Dynamically load a logging handler by its name.

    Args:
        handler_name (str): The name of the handler class to load.
        **kwargs: Additional arguments to pass to the handler.

    Returns:
        logging.Handler: An instance of the requested handler.

    Raises:
        ImportError: If the handler cannot be found.
    """
    try:
        module = importlib.import_module("loghelpers.handlers")
        handler_class = getattr(module, handler_name)
        return handler_class(**kwargs)
    except (AttributeError, ImportError) as e:
        raise ImportError(f"Handler '{handler_name}' could not be loaded: {e}")
