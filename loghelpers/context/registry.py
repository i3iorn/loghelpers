# loghelpers/context/registry.py
from contextlib import contextmanager
from threading import RLock
from typing import Dict

from .protocols import ProviderProtocol
from ..exceptions import (
    InvalidProviderNameException, InvalidProviderException, DuplicateProviderException,
    ProviderNotFoundException
)


class ContextProviders:
    """
    A class to manage context providers for logging.
    This class is used to register and retrieve context providers.
    """
    _lock = RLock()
    _providers = {}

    @classmethod
    def register(cls, name: str, provider: ProviderProtocol) -> None:
        """
        Register a context provider with a given name.
        Args:
            name (str): The name of the context provider.
            provider (ProviderProtocol): The context provider instance to register.

        Returns:

        """
        if not isinstance(provider, ProviderProtocol):
            raise InvalidProviderException(name, "Provider must implement ProviderProtocol")
        if not name or not isinstance(name, str):
            raise InvalidProviderNameException(name)
        if name in cls.all():
            raise DuplicateProviderException(name)
        with cls._lock:
            cls._providers[name] = provider

    @classmethod
    def unregister(cls, name: str) -> None:
        """
        Unregister a context provider by its name.

        :param name: The name of the context provider to unregister.
        """
        with cls._lock:
            if name in cls._providers:
                del cls._providers[name]
            else:
                raise ProviderNotFoundException(name)

    @classmethod
    def get(cls, name, strict: bool = False) -> ProviderProtocol | None:
        """
        Retrieve a registered context provider by its name.

        Args:
            name (str): The name of the context provider to retrieve.
            strict (bool): If True, raises an exception if the provider is not found.
        Returns:
            ProviderProtocol | None: The context provider instance if found, otherwise None.
        """
        with cls._lock:
            if name not in cls._providers:
                if strict:
                    raise ProviderNotFoundException(name)
                return None
            return cls._providers[name]

    @classmethod
    def all(cls) -> Dict[str, ProviderProtocol]:
        """
        Get all registered context providers.

        Returns:
            Dict[str, ProviderProtocol]: A dictionary of all registered context providers.
        """
        with cls._lock:
            return cls._providers

    @classmethod
    def clear(cls) -> None:
        """
        Clear all registered context providers.
        This is useful for resetting the context providers during testing or reconfiguration.
        """
        with cls._lock:
            cls._providers.clear()

    @classmethod
    def reset(cls) -> None:
        """
        Reset the context providers registry except for the default ones.
        """
        with cls._lock:
            cls._providers = {
                "default": cls._providers.get("default", None),
            }

    @classmethod
    def has(cls, name: str) -> bool:
        """
        Check if a context provider with the given name is registered.

        Args:
            name (str): The name of the context provider to check.

        Returns:
            bool: True if the provider is registered, False otherwise.
        """
        with cls._lock:
            return name in cls._providers

    @classmethod
    def gather(cls) -> Dict[str, ProviderProtocol]:
        """
        Gather all registered context providers and return them as a dictionary.

        Returns:
            Dict[str, ProviderProtocol]: A dictionary of all registered context providers.
        """
        with cls._lock:
            return cls._providers.copy()

    @classmethod
    @contextmanager
    def temporary_provider(cls, name: str, provider: ProviderProtocol):
        old = cls.get(name, strict=False)
        cls.register(name, provider)
        try:
            yield
        finally:
            cls.unregister(name)
            if old:
                cls.register(name, old)