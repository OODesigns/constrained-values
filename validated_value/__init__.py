"""
Validated Value Library

A Python library for creating validated value objects with type checking, 
range validation, and enum validation capabilities.
"""
from .status import Status
from .response import Response, T
from .value import (
    Value,
    ValidationStrategy,
    ConstrainedValue,
)
from .ConstrainedValue_types import (
    ConstrainedEnumValue,
    ConstrainedRangeValue,
    StrictValidatedValue
)
from .strategies import (
    TypeValidationStrategy,
    RangeValidationStrategy,
    EnumValidationStrategy
)

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
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
    "StrictValidatedValue",
]

