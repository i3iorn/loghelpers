# loghelpers/utils.py
import re
from enum import Enum


def get_root_path() -> str:
    """
    Get the root path of the project.

    Returns:
        str: The root path of the project.
    """
    import os
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class BatchForegroundColors(Enum):
    WHITE = "\033[37m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    GREY = "\033[0m"
    GREEN = "\033[32m"
    MAGENTA = "\033[35m"
    BLUE = "\033[34m"


class BatchBackgroundColors(Enum):
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    GREY = "\033[100m"
    MAGENTA = "\033[45m"
    WHITE = "\033[47m"
    BLACK = "\033[40m"

