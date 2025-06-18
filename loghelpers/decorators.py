# loghelpers/decorators.py
import logging
import functools
from .utils import get_logger
from contextlib import ContextDecorator
from typing import Optional


class temporary_level(ContextDecorator):
    """Temporarily set logging level for a logger or handlers."""
    def __init__(self, level: int, logger_name: Optional[str] = None):
        self.level = level
        self.logger = logging.getLogger(logger_name) if logger_name else logging.getLogger()
        self.old_level = self.logger.level if hasattr(self.logger, 'level') else logging.NOTSET

    def __enter__(self):
        self.old_levels = [h.level for h in self.logger.handlers]
        self.logger.setLevel(self.level)
        for h in self.logger.handlers:
            h.setLevel(self.level)

    def __exit__(self, exc_type, exc, tb):
        for handler, old in zip(self.logger.handlers, self.old_levels):
            handler.setLevel(old)
        if hasattr(self.logger, 'level'):
            self.logger.setLevel(self.old_level)


def log_calls(level: int = None):
    def decorator(fn):
        logger = get_logger(fn.__module__)
        lvl = level or logger.level

        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            logger.log(lvl, f"→ Enter {fn.__name__} args={args} kwargs={kwargs}")
            try:
                result = fn(*args, **kwargs)
            except Exception as e:
                logger.exception(f"‼ Exception in {fn.__name__}")
                raise
            else:
                logger.log(lvl, f"← Exit {fn.__name__} returned={result!r}")
                return result

        return wrapper
    return decorator
