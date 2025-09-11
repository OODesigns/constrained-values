from typing import Any

from .response import Response, StatusResponse
from .status import Status
from .value import ValidationStrategy
from .constants import DEFAULT_SUCCESS_MESSAGE

def get_types(the_types) -> tuple[Any, ...]:
    if not isinstance(the_types, (list, tuple)):
        the_types = (the_types,)
    return tuple(the_types)

class TypeValidationStrategy(ValidationStrategy):
    def __init__(self, valid_types):
        self.valid_types = get_types(valid_types)

    def validate(self, value) -> Response:
        if type(value) not in self.valid_types:
            # Build a friendly list of type names
            type_names = [t.__name__ for t in self.valid_types]
            types_str = ",".join(f"'{name}'" for name in type_names)
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be one of {types_str}, got '{type(value).__name__}'"
            )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

class SameTypeValidationStrategy(ValidationStrategy):
    def __init__(self, value_a, value_b):
         self.value_a = value_a
         self.value_b = value_b

    def validate(self, value) -> Response:
        ta = type(self.value_a)
        tb = type(self.value_b)
        if ta is not tb:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"value:{self.value_a} must match Type of value:{self.value_b}, as type '{type(self.value_b).__name__}'"
                )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

class RangeValidationStrategy(ValidationStrategy):
    def __init__(self, low_value, high_value):
        self.low_value = low_value
        self.high_value = high_value

    def validate(self, value) -> Response:
        if value < self.low_value:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be greater than or equal to {self.low_value}, got {value}"
            )
        if value > self.high_value:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be less than or equal to {self.high_value}, got {value}"
            )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)


class EnumValidationStrategy(ValidationStrategy):
    def __init__(self, valid_values):
        self.valid_values = valid_values

    def validate(self, value) -> Response:
        if value not in self.valid_values:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_values}, got {value}"
                )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

