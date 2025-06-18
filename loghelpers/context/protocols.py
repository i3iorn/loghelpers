# loghelpers/context/protocols.py
from typing import runtime_checkable, Protocol, Dict


@runtime_checkable
class ProviderProtocol(Protocol):
    """
    Protocol for context providers.
    A context provider should implement a callable that returns a dictionary of context data.
    """

    def __call__(self) -> Dict[str, str]:
        """
        Call the context provider to retrieve context data.
        This method should return a dictionary where keys are context variable names
        and values are their corresponding values.
        Returns:
            Dict[str, str]: A dictionary containing context data.
        """
        raise NotImplementedError("Context providers must implement the __call__ method.")
