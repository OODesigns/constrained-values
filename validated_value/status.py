from enum import Enum


class Status(Enum):
    """
    Enum to represent the status of a process.
    """
    OK = 0
    EXCEPTION = 1