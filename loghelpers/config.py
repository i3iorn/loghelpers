# loghelpers/config.py
import enum
import logging
import re
from dataclasses import dataclass, field
from threading import RLock
from typing import Optional, Any, Set
from pathlib import Path

from .exceptions import (
    InvalidConfigurationKeyException,
    UnsupportedConfigurationFormatException,
    ConfigurationLoadException
)
from .redaction import Redactor
from .utils import get_root_path

TRACE_LEVEL = 5
SUCCESS_LEVEL = 25

logging.addLevelName(TRACE_LEVEL, "TRACE")
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)


def success(self, message, *args, **kwargs):
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)


# Monkey patch the Logger class
logging.Logger.trace = trace
logging.Logger.success = success


SENSITIVE_KEYS = {"password", "token", "secret", "ssn", "email"}

# ISO date pattern for YYYY-MM-DD format which only matches valid dates
ISO_DATE_PATTERN = r'^(?:(?:19|20)\d{2}-(?:(?:0[1-9]|1[0-2])-(?:0[1-9]|[12][0-9]|3[01]))|(?:0[1-9]|[12][0-9]|3[01])-(?:0[1-9]|1[0-2])-(?:19|20)\d{2})$'
SWEDISH_SOCIAL_SECURITY_NUMBER_PATTERN = ISO_DATE_PATTERN + r'[+-]?\d{4}$'

SENSITIVE_PATTERNS = [
    SWEDISH_SOCIAL_SECURITY_NUMBER_PATTERN
]


class Feature(enum.Flag):
    """
    Enum to represent features that can be enabled or disabled.
    """
    NONE = 0
    ALLOW_PROVIDER_OVERWRITE = enum.auto()


_CONFIG_LOADER_MAP = {
    "json": "orjson",
    "yaml": "yaml",
    "yml": "yaml",
    "toml": "toml",
}


@dataclass
class Configuration:
    features: Feature = Feature.NONE
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = str(Path(get_root_path()) / "app.log")
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    sample_rate: float = 1.0
    redactor: Redactor = field(default_factory=lambda: Redactor(
        sensitive_keys=SENSITIVE_KEYS,
        redact_value_patterns=SENSITIVE_PATTERNS
    ))
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def __post_init__(self):
        """
        Post-initialization to set the logging level.
        """
        self.log_level = self.log_level.upper()
        logging.getLogger().setLevel(self.log_level)

    @property
    def sensitive_keys(self) -> Set[str]:
        """
        Get the set of sensitive keys.

        Returns:
            set[str]: The set of sensitive keys.
        """
        with self._lock:
            return self.redactor.sensitive_keys

    def add_sensitive_key(self, key: str) -> None:
        """
        Add a sensitive key to the configuration.

        Args:
            key (str): The sensitive key to add.
        """
        with self._lock:
            if not isinstance(key, str):
                raise ValueError("Sensitive key must be a string.")
            self.redactor.sensitive_keys.add(key)

    def update_log_level(self, level: str) -> None:
        with self._lock:
            self.log_level = level.upper()
            logging.getLogger().setLevel(self.log_level)

    def update_sample_rate(self, rate: float) -> None:
        with self._lock:
            self.sample_rate = rate

    def update_sensitive_keys(self, keys: set[str]) -> None:
        with self._lock:
            if not isinstance(keys, set):
                raise ValueError("Sensitive keys must be a set.")
            self.redactor.sensitive_keys = keys

    def _get_loader_format(self, file_format: str) -> Any:
        """
        Get the appropriate loader for the given file format.

        Args:
            file_format (str): The format of the configuration file.

        Returns:
            Callable: A function to load the configuration data.
        """
        if file_format in _CONFIG_LOADER_MAP:
            try:
                if _CONFIG_LOADER_MAP[file_format] == "orjson":
                    import orjson
                    return orjson.loads
                elif _CONFIG_LOADER_MAP[file_format] == "yaml":
                    import yaml
                    return yaml.safe_load
                elif _CONFIG_LOADER_MAP[file_format] == "toml":
                    import toml
                    return toml.load
            except ModuleNotFoundError as e:
                raise UnsupportedConfigurationFormatException(
                    f"Required module for {file_format} format is not installed: {e}"
                )

        raise UnsupportedConfigurationFormatException(file_format)

    def from_file(self, file_path: str) -> None:
        """
        Load configuration from a file.

        Args:
            file_path (str): Path to the configuration file.
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, 'r') as f:
            file_format = file_path.suffix[1:].lower()
            loader = self._get_loader_format(file_format)

            try:
                config_data = loader(f.read())
            except Exception as e:
                raise ConfigurationLoadException(f"Failed to load configuration from {file_path}: {e}")

            if not isinstance(config_data, dict):
                raise InvalidConfigurationKeyException(f"Configuration file {file_path} must contain a dictionary.")

            for key, value in config_data.items():
                if hasattr(self, key):
                    setattr(self, key, value)
                else:
                    raise InvalidConfigurationKeyException(f"Invalid configuration key: {key}")

    def validate(self) -> None:
        """
        Validate the configuration values.
        """
        if self.sample_rate < 0.0 or self.sample_rate > 1.0:
            raise ValueError("Sample rate must be between 0.0 and 1.0.")

        if not isinstance(self._sensitive_keys, set):
            raise ValueError("Sensitive keys must be a set.")

        if not isinstance(self.log_level, str):
            raise ValueError("Log level must be a string.")


class FeatureManager:
    _instance: Optional["FeatureManager"] = None

    def __new__(cls, config: Configuration):
        if cls._instance is None:
            cls._instance = super(FeatureManager, cls).__new__(cls)
            cls._instance.config = config
        return cls._instance

    def is_enabled(self, feature: Feature) -> bool:
        return feature in self.config.features

    def enable(self, feature: Feature) -> None:
        self.config.features |= feature

    def disable(self, feature: Feature) -> None:
        self.config.features &= ~feature
