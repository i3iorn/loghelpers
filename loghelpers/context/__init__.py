# loghelpers/context/__init__.py
import contextvars
from contextlib import contextmanager
from typing import Dict, Generator

from ..config import Feature, Configuration
from ..context.default_provider import DefaultProvider
from ..context.registry import ContextProviders
from ..exceptions import ProviderExecutionException, DuplicateProviderKeyException

ContextProviders.register("default", DefaultProvider())


# Update the log record factory to handle more context variables
"""
old_factory = logging.getLogRecordFactory()

def record_factory(*args, **kwargs):
    record = old_factory(*args, **kwargs)
    record.custom_attribute = 0xdecafbad
    return record

logging.setLogRecordFactory(record_factory)
"""

class LoggingContext:
    """
    A context-local storage for managing contextual data in logs.

    Uses `contextvars` to ensure proper behavior in both threaded and async environments.
    """

    _context_var: contextvars.ContextVar[Dict[str, str]] = contextvars.ContextVar("log_context")

    @classmethod
    def set_context(cls, **kwargs: str) -> None:
        """
        Set or update context variables.

        Args:
            **kwargs: Key-value pairs to set in the logging context.
        """
        context = cls.get_context().copy()
        context.update(kwargs)
        cls._context_var.set(context)

    @classmethod
    def get_context(cls) -> Dict[str, str]:
        """
        Get the current context.

        Returns:
            A dictionary representing the current logging context.
        """
        try:
            return cls._context_var.get()
        except LookupError:
            return {}

    @classmethod
    def clear_context(cls) -> None:
        """
        Clear all context variables.
        """
        cls._context_var.set({})

    @classmethod
    @contextmanager
    def context(cls, **kwargs: str) -> Generator[None, None, None]:
        """
        Context manager for temporarily setting contextual data.

        Args:
            **kwargs: Key-value pairs to set temporarily in the logging context.

        Yields:
            None
        """
        token = cls._context_var.set({**cls._context_var.get(), **kwargs})
        try:
            yield
        finally:
            cls._context_var.reset(token)

    def resolve_context(self, config: Configuration) -> Dict[str, str]:
        """
        Return the merged context from current values and registered providers.

        Does not mutate the active context.

        Args:
            config: The logging configuration.

        Returns:
            A merged context dictionary.
        """
        base_context = self.get_context().copy()
        providers = ContextProviders.gather()

        print(providers, config.features)

        for name, provider in providers.items():
            try:
                result = provider()
            except Exception as e:
                raise ProviderExecutionException(name, e)

            for key, value in result.items():
                if key not in base_context:
                    base_context[key] = value
                elif config.features.is_enabled(Feature.MUTABLE_PROVIDER_KEYS):
                    base_context[key] = value
                else:
                    raise DuplicateProviderKeyException(name, key)

        return base_context

