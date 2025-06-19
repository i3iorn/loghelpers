import pytest

from loghelpers.context import ContextProviders
from loghelpers.exceptions import InvalidProviderException, \
    InvalidProviderNameException, DuplicateProviderException, ProviderNotFoundException


class MockProvider:
    def __call__(self):
        return {"key": "value"}


def test_register_raises_exception_for_invalid_provider():
    with pytest.raises(InvalidProviderException):
        ContextProviders.register("invalid", object())

def test_register_raises_exception_for_invalid_name():
    with pytest.raises(InvalidProviderNameException):
        ContextProviders.register("", MockProvider())

def test_register_raises_exception_for_duplicate_provider():
    provider = MockProvider()
    ContextProviders.register("duplicate", provider)
    with pytest.raises(DuplicateProviderException):
        ContextProviders.register("duplicate", provider)
    ContextProviders.unregister("duplicate")

def test_unregister_raises_exception_for_nonexistent_provider():
    with pytest.raises(ProviderNotFoundException):
        ContextProviders.unregister("nonexistent")

def test_get_returns_none_for_nonexistent_provider_when_not_strict():
    assert ContextProviders.get("nonexistent", strict=False) is None

def test_get_raises_exception_for_nonexistent_provider_when_strict():
    with pytest.raises(ProviderNotFoundException):
        ContextProviders.get("nonexistent", strict=True)

def test_clear_removes_all_providers():
    ContextProviders.register("provider1", MockProvider())
    ContextProviders.register("provider2", MockProvider())
    ContextProviders.clear()
    assert not ContextProviders.all()

def test_reset_keeps_only_default_provider():
    ContextProviders.register("provider1", MockProvider())
    ContextProviders.reset()
    assert "default" in ContextProviders.all()
    assert len(ContextProviders.all()) == 1

def test_has_returns_true_for_registered_provider():
    ContextProviders.register("existing", MockProvider())
    assert ContextProviders.has("existing")
    ContextProviders.unregister("existing")

def test_has_returns_false_for_unregistered_provider():
    assert not ContextProviders.has("nonexistent")

def test_temporary_provider_registers_and_restores_previous_state():
    original_provider = MockProvider()
    temporary_provider = MockProvider()
    ContextProviders.register("temp", original_provider)
    with ContextProviders.temporary_provider("temp", temporary_provider):
        assert ContextProviders.get("temp") is temporary_provider
    assert ContextProviders.get("temp") is original_provider
    ContextProviders.unregister("temp")