import pytest

from loghelpers.redaction import Redactor


def test_redact_sensitive_keys_in_dict():
    redactor = Redactor(sensitive_keys={"password", "token"})
    data = {"username": "user1", "password": "secret", "token": "abc123"}
    redacted = redactor.redact(data)
    assert redacted["username"] == "user1"
    assert redacted["password"] == "<redacted>"
    assert redacted["token"] == "<redacted>"


def test_redact_sensitive_values_in_list():
    redactor = Redactor(sensitive_keys=set(), redact_value_patterns=[r"\d{4}-\d{4}"])
    data = ["1234-5678", "no-match", "5678-1234"]
    redacted = redactor.redact(data)
    assert redacted == ["<redacted>", "no-match", "<redacted>"]


def test_redact_handles_nested_structures():
    redactor = Redactor(sensitive_keys={"password"}, redact_value_patterns=[r"secret"])
    data = {
        "user": {"name": "Alice", "password": "secret"},
        "logs": ["no secret here", "contains secret"]
    }
    redacted = redactor.redact(data)
    assert redacted["user"]["name"] == "Alice"
    assert redacted["user"]["password"] == "<redacted>"
    assert redacted["logs"] == ["no <redacted> here", "contains <redacted>"]


def test_redact_ignores_non_sensitive_keys():
    redactor = Redactor(sensitive_keys={"password"})
    data = {"username": "user1", "email": "user1@example.com"}
    redacted = redactor.redact(data)
    assert redacted == data


def test_redact_for_none_set_iterable_keys():
    Redactor(sensitive_keys=["not_a_set"])


def test_redact_raises_error_for_invalid_redact_patterns():
    with pytest.raises(ValueError):
        redactor = Redactor(sensitive_keys=set())
        redactor.redact_patterns = "not_a_list"


def test_redact_raises_error_for_invalid_redaction_token():
    with pytest.raises(ValueError):
        redactor = Redactor(sensitive_keys=set())
        redactor.redaction_token = 123
