"""
Validated Value Library

A Python library for creating validated value objects with type checking,
range validation, and enum validation capabilities.
"""

from .constants import DEFAULT_SUCCESS_MESSAGE
from .status import Status
from .response import Response, T
from .value import Value, ValidationStrategy, ConstrainedValue
from .constrained_value_types import (
    ConstrainedEnumValue,
    ConstrainedRangeValue,
    StrictConstrainedValue,
)
from .strategies import (
    TypeValidationStrategy,
    RangeValidationStrategy,
    EnumValidationStrategy,
)

__version__ = "0.1.1"

__all__ = [
    "DEFAULT_SUCCESS_MESSAGE",
    "Status",
    "Response",
    "Value",
    "ValidationStrategy",
    "TypeValidationStrategy",
    "RangeValidationStrategy",
    "EnumValidationStrategy",
    "ConstrainedValue",
    "ConstrainedEnumValue",
    "ConstrainedRangeValue",
    "StrictConstrainedValue",
]
