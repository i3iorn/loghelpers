# loghelpers/config.py
import enum
import logging
from dataclasses import dataclass, field
from threading import RLock
from .utils import get_root_path

TRACE_LEVEL = 5
logging.addLevelName(TRACE_LEVEL, "TRACE")

def trace(self, message, *args, **kwargs):
    if self.isEnabledFor(TRACE_LEVEL):
        self._log(TRACE_LEVEL, message, args, **kwargs)

logging.Logger.trace = trace  # monkey patch

SENSITIVE_KEYS = {"password", "token", "secret", "ssn", "email"}


class Feature(enum.Flag):
    """
    Enum to represent features that can be enabled or disabled.
    """
    NONE = 0
    ALLOW_PROVIDER_OVERWRITE = enum.auto()


@dataclass
class Configuration:
    features: Feature = Feature.NONE
    debug: bool = False
    log_level: str = "INFO"
    log_file: str = get_root_path() + "app.log"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    sample_rate: float = 1.0
    sensitive_keys: set[str] = field(default_factory=lambda: SENSITIVE_KEYS)
    _lock: RLock = field(default_factory=RLock, init=False, repr=False)

    def update_log_level(self, level: str):
        with self._lock:
            self.log_level = level.upper()
            logging.getLogger().setLevel(self.log_level)

    def update_sample_rate(self, rate: float):
        with self._lock:
            self.sample_rate = rate

    def update_sensitive_keys(self, keys: set[str]):
        with self._lock:
            self.sensitive_keys = keys
