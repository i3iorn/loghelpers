import pytest
import logging

from loghelpers import ColorFormatter, JsonFormatter, Configuration
from loghelpers.context import LoggingContext, ContextProviders
from loghelpers.utils import BatchForegroundColors


@pytest.fixture
def default_config() -> Configuration:
    """Fixture to provide a default configuration for testing."""
    return Configuration(
        log_level="INFO",
        log_format="%(message)s",
    )


def test_json_formatter_formats_log_record_into_json(default_config):
    formatter = JsonFormatter(default_config)
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert '"logger":"test_logger"' in formatted
    assert '"level":"INFO"' in formatted
    assert '"message":"Test message"' in formatted

def test_json_formatter_includes_context_in_payload(default_config):
    formatter = JsonFormatter(default_config)
    LoggingContext.set_context(user="Alice", action="login")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert '"user":"Alice"' in formatted
    assert '"action":"login"' in formatted
    LoggingContext.clear_context()

def test_json_formatter_redacts_sensitive_keys(default_config):
    formatter = JsonFormatter(default_config)
    def sensitive_provider():
        return {"sensitive_data": "secret_value"}
    ContextProviders.register("sensitive", sensitive_provider)
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname=__file__,
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    default_config.add_sensitive_key("sensitive_data")
    formatted = formatter.format(record)
    assert '"sensitive_data":"<redacted>"' in formatted

def test_color_formatter_adds_ansi_colors_based_on_level(default_config):
    formatter = ColorFormatter("%(message)s")
    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname=__file__,
        lineno=10,
        msg="Error occurred",
        args=(),
        exc_info=None
    )
    formatted = formatter.format(record)
    assert BatchForegroundColors.RED.value in formatted
    assert BatchForegroundColors.GREY.value in formatted
    assert "Error occurred" in formatted