from decimal import Decimal
from fractions import Fraction
from typing import Any, Sequence, Tuple

from .response import StatusResponse, Response
from .status import Status
from .value import ValidationStrategy, TransformationStrategy
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

class CoerceToType(TransformationStrategy[object, object]):
    """
    Coerce the current value to a concrete target type (usually type(low_value)),
    so range comparisons are performed like-for-like.

    Examples:
      - int -> float
      - int/float/str -> Decimal
      - int/float -> Fraction

    Notes:
      - Converting float -> Decimal can carry binary fp artifacts; consider tightening if needed.
      - bool is a subclass of int; decide whether you want to accept it upstream.
    """
    __slots__ = ("_target_type",)

    def __init__(self, target_type: type):
        self._target_type = target_type

    def transform(self, value: object) -> Response[object]:
        # Already desired type
        if isinstance(value, self._target_type):
            return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)

        try:
            # Common numeric normalizations
            if self._target_type is float and isinstance(value, int):
                return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=float(value))

            if self._target_type is Decimal:
                # Choose your policy re: floats -> Decimal; str(...) avoids binary artifacts.
                if isinstance(value, float):
                    coerced = Decimal(str(value))
                else:
                    coerced = Decimal(value)  # handles int/str/Decimal
                return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=coerced)

            if self._target_type is Fraction:
                return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=Fraction(value))

            # Generic fallback: attempt constructor
            coerced = self._target_type(value)
            return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=coerced)

        except Exception as e:
            return Response(status=Status.EXCEPTION, details=str(e), value=None)


class FailValidationStrategy(ValidationStrategy[str]):
    """First-class strategy that fails immediately with a human-readable message."""
    __slots__ = ("_details",)

    def __init__(self, details: str):
        self._details = details

    def validate(self, value: Any) -> StatusResponse:
        return StatusResponse(status=Status.EXCEPTION, details=self._details)
