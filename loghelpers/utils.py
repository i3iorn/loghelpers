# loghelpers/utils.py
import logging
from enum import Enum

from .config import SENSITIVE_KEYS, Configuration
from .handlers import create_file_handler, create_console_handler


def get_root_path() -> str:
    """
    Get the root path of the project.

    Returns:
        str: The root path of the project.
    """
    import os
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BatchForegroundColors(Enum):
    WHITE = "\033[37m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    GREY = "\033[0m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"


class BatchBackgroundColors(Enum):
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    GREY = "\033[100m"
    MAGENTA = "\033[45m"
    WHITE = "\033[47m"
    BLACK = "\033[40m"


def redact(payload: dict) -> dict:
    return {
        k: ("<redacted>" if k.lower() in SENSITIVE_KEYS else v)
        for k, v in payload.items()
    }


def setup_logging(config: Configuration) -> None:
    """
    Sets up the logging configuration using the provided Configuration object.

    Args:
        config (Configuration): The configuration to use.
    """

    logger = logging.getLogger()
    logger.setLevel(config.log_level)

    logger.handlers.clear()
    logger.addHandler(create_console_handler(config))
    logger.addHandler(create_file_handler(config))


def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger with the specified name.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: The logger instance.
    """
    return logging.getLogger(name)