# loghelpers/exceptions.py
class ContextProviderException(Exception):
    """Base class for all context provider exceptions."""
    pass


class ProviderNotFoundException(ContextProviderException):
    """Raised when a requested context provider is not found."""

    def __init__(self, provider_name: str):
        super().__init__(f"Context provider '{provider_name}' not found.")
        self.provider_name = provider_name

class ProviderInitializationException(ContextProviderException):
    """Raised when a context provider fails to initialize."""

    def __init__(self, provider_name: str, reason: str):
        super().__init__(f"Context provider '{provider_name}' failed to initialize: {reason}")
        self.provider_name = provider_name
        self.reason = reason


class ProviderExecutionException(ContextProviderException):
    """Raised when a context provider execution fails."""

    def __init__(self, provider_name: str, e: Exception):
        super().__init__(f"Context provider '{provider_name}' execution failed: {str(e)}")
        self.provider_name = provider_name
        self.original_exception = e


class DuplicateProviderKeyException(ContextProviderException):
    """Raised when a duplicate key is found in a context provider's data."""

    def __init__(self, provider_name: str, key: str):
        super().__init__(f"Duplicate key '{key}' found in context provider '{provider_name}'.")
        self.provider_name = provider_name
        self.key = key


class InvalidProviderNameException(ContextProviderException):
    """Raised when an invalid provider name is used."""

    def __init__(self, provider_name: str):
        super().__init__(f"Invalid context provider name: '{provider_name}'")
        self.provider_name = provider_name


class InvalidProviderException(ContextProviderException):
    """Raised when a provider does not conform to the expected interface."""

    def __init__(self, provider_name: str, reason: str):
        super().__init__(f"Context provider '{provider_name}' is invalid: {reason}")
        self.provider_name = provider_name
        self.reason = reason


class DuplicateProviderException(ContextProviderException):
    """Raised when a duplicate context provider is registered."""

    def __init__(self, provider_name: str):
        super().__init__(f"Context provider '{provider_name}' is already registered.")
        self.provider_name = provider_name


class ConfigurationException(Exception):
    """Base class for configuration-related exceptions."""
    pass


class InvalidConfigurationKeyException(ConfigurationException):
    """Raised when a configuration key is invalid."""

    def __init__(self, key: str):
        super().__init__(f"Invalid configuration key: '{key}'")
        self.key = key


class UnsupportedConfigurationFormatException(ConfigurationException):
    """Raised when an unsupported configuration format is encountered."""

    def __init__(self, format: str):
        super().__init__(f"Unsupported configuration format: '{format}'")
        self.format = format


class ConfigurationLoadException(ConfigurationException):
    """Raised when a configuration file fails to load."""
    pass
