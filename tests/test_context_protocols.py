import pytest

from typing import Dict

from loghelpers.context.protocols import ProviderProtocol


def test_provider_protocol_allows_valid_implementation():
    class ValidProvider:
        def __call__(self) -> Dict[str, str]:
            return {"key": "value"}

    provider = ValidProvider()
    assert isinstance(provider, ProviderProtocol)

def test_provider_protocol_rejects_invalid_implementation():
    class InvalidProvider:
        def not_call(self) -> Dict[str, str]:
            return {"key": "value"}

    provider = InvalidProvider()
    assert not isinstance(provider, ProviderProtocol)