import re
from typing import Any, Dict, List, Protocol, Union, runtime_checkable, Set


@runtime_checkable
class Redactable(Protocol):
    """
    Protocol for objects that can define their own redacted representation.
    """
    def __redact__(self) -> Any:
        ...


class Sensitive:
    """
    Wraps a value that should be redacted when serialized or logged.
    """
    def __init__(self, value: Any):
        self._value = value

    def __redact__(self) -> str:
        return "<redacted>"

    def __str__(self) -> str:
        return "<redacted>"

    def __repr__(self) -> str:
        return "<redacted>"


class Redactor:
    """
    Redacts sensitive data from structured and unstructured objects.
    Supports recursive redaction, regex matches, and custom object handling.
    """

    def __init__(
        self,
        sensitive_keys: Set[str],
        redact_value_patterns: List[str] = None,
        redaction_token: str = "<redacted>"
    ):
        """
        Initialize the redactor.

        Args:
            sensitive_keys: List of keys to redact from dict-like structures.
            redact_value_patterns: Optional list of regex patterns to redact from strings.
            redaction_token: The token to use when redacting.
        """
        self._sensitive_keys = set(k.lower() for k in sensitive_keys)
        self._redact_patterns = [re.compile(p, re.IGNORECASE) for p in (redact_value_patterns or [])]
        self._redaction_token = redaction_token

    @property
    def sensitive_keys(self) -> Set[str]:
        """
        Get the set of sensitive keys.

        Returns:
            Set[str]: The set of sensitive keys.
        """
        return self._sensitive_keys

    @property
    def redact_patterns(self) -> List[re.Pattern]:
        """
        Get the list of regex patterns used for redaction.

        Returns:
            List[re.Pattern]: The list of compiled regex patterns.
        """
        return self._redact_patterns

    @property
    def redaction_token(self) -> str:
        """
        Get the redaction token used for redacting sensitive data.

        Returns:
            str: The redaction token.
        """
        return self._redaction_token

    @sensitive_keys.setter
    def sensitive_keys(self, keys: Set[str]) -> None:
        """
        Set the sensitive keys for redaction.

        Args:
            keys: A set of keys to be considered sensitive.
        """
        if not isinstance(keys, set):
            raise ValueError("Sensitive keys must be a set.")
        self._sensitive_keys = set(k.lower() for k in keys)

    @redact_patterns.setter
    def redact_patterns(self, patterns: List[str]) -> None:
        """
        Set the regex patterns used for redaction.

        Args:
            patterns: A list of regex patterns to be used for redaction.
        """
        if not isinstance(patterns, list):
            raise ValueError("Redact patterns must be a list.")
        self._redact_patterns = [re.compile(p, re.IGNORECASE) for p in patterns]

    @redaction_token.setter
    def redaction_token(self, token: str) -> None:
        """
        Set the redaction token.

        Args:
            token: The string to use for redacting sensitive data.
        """
        if not isinstance(token, str):
            raise ValueError("Redaction token must be a string.")
        self._redaction_token = token

    def redact(self, value: Any) -> Any:
        """
        Redact a given value recursively.

        Args:
            value: Any data to be redacted.

        Returns:
            The redacted value.
        """
        if isinstance(value, Redactable):
            return value.__redact__()

        elif isinstance(value, Sensitive):
            return self.redaction_token

        elif isinstance(value, dict):
            return {
                k: self.redaction_token if k.lower() in self.sensitive_keys else self.redact(v)
                for k, v in value.items()
            }

        elif isinstance(value, list):
            return [self.redact(item) for item in value]

        elif isinstance(value, tuple):
            return tuple(self.redact(item) for item in value)

        elif isinstance(value, str):
            for pattern in self.redact_patterns:
                value = pattern.sub(self.redaction_token, value)
            return value

        return value
