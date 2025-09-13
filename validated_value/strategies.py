from typing import Any, Sequence, Tuple

from .response import StatusResponse
from .status import Status
from .value import ValidationStrategy
from .constants import DEFAULT_SUCCESS_MESSAGE

def get_types(the_types: Any) -> tuple[type, ...]:
    """
    Normalize a single type or a sequence of types into a tuple[type, ...],
    and validate that every item is actually a 'type' object.
    """
    if not isinstance(the_types, (list, tuple)):
        the_types = (the_types,)

    # Validate each item is a runtime 'type' (e.g., int, str, MyClass)
    for t in the_types:
        if not isinstance(t, type):
            raise TypeError(f"valid_types must be types; got {t!r}")

    return tuple(the_types)  # type: ignore[return-value]

class TypeValidationStrategy(ValidationStrategy[Any]):
    """
    Ensure the runtime type of 'value' is one of the allowed types.
    """
    def __init__(self, valid_types: Sequence[type] | type):
        self.valid_types: Tuple[type, ...] = get_types(valid_types)

    def validate(self, value: Any) -> StatusResponse:
        if type(value) not in self.valid_types:
            # Build a friendly list of type names
            types_str = ", ".join(f"'{t.__name__}'" for t in self.valid_types)
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be one of {types_str}, got '{type(value).__name__}'"
            )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

class SameTypeValidationStrategy(ValidationStrategy[Any]):
    """
    Ensure two reference values have the same *type*. Useful when you want 'value'
    to later be compared/combined with similarly-typed sentinels.
    """
    def __init__(self, value_a: Any, value_b: Any):
        self.value_a = value_a
        self.value_b = value_b

    def validate(self, value: Any) -> StatusResponse:
        ta = type(self.value_a)
        tb = type(self.value_b)
        if ta is not tb:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=(
                    f"Type mismatch: expected type '{type(self.value_b).__name__}' of value {self.value_b} "
                    f"to match '{type(self.value_a).__name__}' of value {self.value_a}"
                )
            )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

class RangeValidationStrategy(ValidationStrategy[Any]):
    """
    Validate that 'value' is within [low_value, high_value]. Assumes 'value' and the
    bounds are comparable via '<' and '>'.
    """
    def __init__(self, low_value: Any, high_value: Any):
        self.low_value = low_value
        self.high_value = high_value

    def validate(self, value: Any) -> StatusResponse:
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


class EnumValidationStrategy(ValidationStrategy[Any]):
    """
    Validate that 'value' is one of a provided collection (using membership test).
    """
    def __init__(self, valid_values: Sequence[Any]):
        self.valid_values = valid_values

    def validate(self, value: Any) -> StatusResponse:
        if value not in self.valid_values:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_values}, got {value}"
                )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

