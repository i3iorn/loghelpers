import pytest
import logging

from loghelpers import temporary_level, log_calls

def test_temporary_level_sets_logger_and_handler_levels():
    logger = logging.getLogger("test_logger")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    original_level = logger.level
    handler.setLevel(logging.WARNING)

    with temporary_level(logging.DEBUG, "test_logger"):
        assert logger.level == logging.DEBUG
        assert all(h.level == logging.DEBUG for h in logger.handlers)

    assert logger.level == original_level
    assert handler.level == logging.WARNING


def test_temporary_level_restores_levels_on_exception():
    logger = logging.getLogger("test_logger")
    handler = logging.StreamHandler()
    logger.addHandler(handler)
    original_level = logger.level
    handler.setLevel(logging.WARNING)

    try:
        with temporary_level(logging.DEBUG, "test_logger"):
            assert logger.level == logging.DEBUG
            assert all(h.level == logging.DEBUG for h in logger.handlers)
            raise ValueError("Test exception")
    except ValueError:
        pass

    assert logger.level == original_level
    assert handler.level == logging.WARNING


def test_log_calls_logs_entry_and_exit():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    log_output = []

    def mock_log(level, msg):
        log_output.append((level, msg))

    logger.log = mock_log

    @log_calls(level=logging.INFO, injected_logger=logger)
    def sample_function(x, y):
        return x + y

    result = sample_function(2, 3)
    assert result == 5
    assert len(log_output) == 2
    assert "→ Enter sample_function" in log_output[0][1]
    assert "← Exit sample_function" in log_output[1][1]


def test_log_calls_logs_exceptions():
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.DEBUG)
    log_output = []

    def mock_log(level, msg):
        log_output.append((level, msg))

    logger.log = mock_log
    logger.exception = lambda msg: log_output.append((logging.ERROR, msg))

    @log_calls(level=logging.INFO, injected_logger=logger)
    def sample_function(x, y):
        raise ValueError("Test exception")

    try:
        sample_function(2, 3)
    except ValueError:
        pass

    print("",log_output,"", sep="\n")  # For debugging purposes
    assert len(log_output) >= 2
    assert "→ Enter sample_function" in log_output[0][1]
    assert "‼ Exception in sample_function" in log_output[1][1]