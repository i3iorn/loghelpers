# loghelpers/__init__.py
import logging
from typing import Optional

from .config import Configuration, Feature
from .decorators import log_calls, temporary_level
from .formatters import JsonFormatter, ColorFormatter

__all__ = [
    "Configuration",
    "JsonFormatter",
    "ColorFormatter",
    "log_calls",
]

from .handlers import SensitiveDataFilter


def get_logger(
        *,  # Allow for future expansion without breaking API
        name: Optional[str] = None,
        level: Optional[int] = None,
        config: Optional[Configuration] = None
) -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name of the logger. Defaults to the calling module's name.
        level (int): Logging level to set for the logger. Defaults to INFO.
        config (Configuration): Optional configuration object to use for logger setup.

    Returns:
        logging.Logger: Configured logger instance.
    """
    if name is None:
        name = __name__

    logger = logging.getLogger(name)

    logger.setLevel(level or config.log_level)

    if not config:
        config = Configuration()

    # Set up console handler with color formatter
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level)
    console_handler.setFormatter(ColorFormatter(fmt=config.log_format, style="{"))
    logger.addHandler(console_handler)

    # Set up file handler with JSON formatter
    if config.log_file:
        file_handler = logging.FileHandler(config.log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(config.log_level)
        file_handler.setFormatter(JsonFormatter(config))
        logger.addHandler(file_handler)

    # Add sensitive data filter if configured
    if Feature.REDACT_SENSITIVE_DATA in config.features:
        sensitive_filter = SensitiveDataFilter(config)
        for handler in logger.handlers:
            handler.addFilter(sensitive_filter)

    return logger
