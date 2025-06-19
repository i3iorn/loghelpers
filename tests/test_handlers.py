import logging
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

import pytest

from loghelpers import Configuration
from loghelpers import JsonFormatter, ColorFormatter
from loghelpers.handlers import load_handler, SensitiveDataFilter, create_file_handler, \
    create_console_handler


@pytest.fixture
def default_config():
    return Configuration(
        log_level="INFO",
        log_file="test.log",
        log_format="%(message)s"
    )


def test_create_console_handler_applies_color_formatter(default_config):
    handler = create_console_handler(default_config)
    assert isinstance(handler.formatter, ColorFormatter)
    assert handler.formatter._fmt == "[{levelname}] {message}"
    assert handler.level == logging.getLevelName(default_config.log_level)


def test_create_console_handler_applies_sensitive_data_filter(default_config):
    handler = create_console_handler(default_config)
    assert any(isinstance(f, SensitiveDataFilter) for f in handler.filters)


def test_create_file_handler_creates_rotating_file_handler(default_config, tmp_path):
    default_config.log_file = str(tmp_path / "test.log")
    handler = create_file_handler(default_config)
    assert isinstance(handler, RotatingFileHandler)
    assert handler.baseFilename == default_config.log_file
    assert handler.maxBytes == 5 * 1024 * 1024
    assert handler.backupCount == 3


def test_create_file_handler_applies_json_formatter(default_config, tmp_path):
    default_config.log_file = str(tmp_path / "test.log")
    handler = create_file_handler(default_config)
    assert isinstance(handler.formatter, JsonFormatter)


def test_create_file_handler_applies_sensitive_data_filter(default_config, tmp_path):
    default_config.log_file = str(tmp_path / "test.log")
    handler = create_file_handler(default_config)
    assert any(isinstance(f, SensitiveDataFilter) for f in handler.filters)


def test_load_handler_dynamically_loads_valid_handler():
    handler = load_handler("StreamHandler")
    assert isinstance(handler, StreamHandler)


def test_load_handler_raises_exception_for_invalid_handler():
    with pytest.raises(ImportError):
        load_handler("InvalidHandler")
