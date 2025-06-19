# loghelpers/context/default_provider.py
import inspect
import os
import sys
from typing import Dict


class DefaultProvider:
    """
    Default context provider that returns an empty dictionary.
    This can be used when no specific context is needed.
    """

    def __call__(self) -> Dict[str, str]:
        """
        Returns default context from the system and environment using the os, sys, and
        inspect modules.

        Returns:
            Dict[str, str]: An empty dictionary.
        """
        return {
            "os": os.name,
            "sys_platform": sys.platform,
            "python_version": sys.version,
            "current_file": inspect.getfile(inspect.currentframe()) if inspect.currentframe() else None,
            "current_function": inspect.currentframe().f_code.co_name if inspect.currentframe() else None,
        }
