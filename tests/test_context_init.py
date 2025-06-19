import pytest

from loghelpers import Configuration
from loghelpers.config import Feature
from loghelpers.context import LoggingContext, ContextProviders
from loghelpers.exceptions import DuplicateProviderKeyException, \
    ProviderExecutionException


def test_set_context_updates_existing_keys():
    LoggingContext.set_context(user="Alice", action="login")
    LoggingContext.set_context(action="logout")
    context = LoggingContext.get_context()
    assert context["user"] == "Alice"
    assert context["action"] == "logout"

def test_set_context_adds_new_keys():
    LoggingContext.set_context(user="Alice")
    LoggingContext.set_context(action="login")
    context = LoggingContext.get_context()
    assert context["user"] == "Alice"
    assert context["action"] == "login"

def test_get_context_returns_empty_dict_when_no_context_set():
    LoggingContext.clear_context()
    context = LoggingContext.get_context()
    assert context == {}

def test_clear_context_removes_all_keys():
    LoggingContext.set_context(user="Alice", action="login")
    LoggingContext.clear_context()
    context = LoggingContext.get_context()
    assert context == {}

def test_context_manager_temporarily_sets_context():
    LoggingContext.set_context(user="Alice")
    with LoggingContext.context(action="login"):
        context = LoggingContext.get_context()
        assert context["user"] == "Alice"
        assert context["action"] == "login"
    context = LoggingContext.get_context()
    assert "action" not in context
    assert context["user"] == "Alice"

def test_resolve_context_merges_providers_and_context():
    config = Configuration()
    LoggingContext.set_context(user="Alice")
    ContextProviders.register("provider1", lambda: {"action": "login"})
    context = LoggingContext().resolve_context(config)
    assert context["user"] == "Alice"
    assert context["action"] == "login"
    ContextProviders.unregister("provider1")

def test_resolve_context_allows_provider_overwrite_when_enabled():
    config = Configuration()
    config.features.enable(Feature.MUTABLE_PROVIDER_KEYS)
    LoggingContext.set_context(user="Alice")
    ContextProviders.register("provider1", lambda: {"user": "Bob"})
    context = LoggingContext().resolve_context(config)
    assert context["user"] == "Bob"
    ContextProviders.unregister("provider1")

def test_resolve_context_raises_exception_on_duplicate_keys_when_not_allowed():
    config = Configuration()
    LoggingContext.set_context(user="Alice")
    ContextProviders.register("provider1", lambda: {"user": "Bob"})
    config.features.disable(Feature.MUTABLE_PROVIDER_KEYS)
    with pytest.raises(DuplicateProviderKeyException):
        LoggingContext().resolve_context(config)
    ContextProviders.unregister("provider1")

def test_resolve_context_handles_provider_exceptions_gracefully():
    config = Configuration()
    ContextProviders.register("provider1", lambda: 1 / 0)
    with pytest.raises(ProviderExecutionException):
        LoggingContext().resolve_context(config)
    ContextProviders.unregister("provider1")