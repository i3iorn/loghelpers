import pytest
import inspect

from loghelpers.context import DefaultProvider


def test_default_provider_returns_expected_context():
    provider = DefaultProvider()
    context = provider()
    assert "os" in context
    assert "sys_platform" in context
    assert "python_version" in context
    assert "current_file" in context
    assert "current_function" in context

def test_default_provider_handles_missing_inspect_frame():
    provider = DefaultProvider()
    original_currentframe = inspect.currentframe
    inspect.currentframe = lambda: None  # Simulate missing frame
    context = provider()
    assert context["current_file"] is None
    assert context["current_function"] is None
    inspect.currentframe = original_currentframe  # Restore original function
