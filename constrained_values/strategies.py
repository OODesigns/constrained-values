from decimal import Decimal
from fractions import Fraction
from typing import Any, Sequence, Tuple

from .response import StatusResponse, Response
from .status import Status
from .value import ValidationStrategy, TransformationStrategy
from .constants import DEFAULT_SUCCESS_MESSAGE


def get_types(the_types: Any) -> tuple[type, ...]:
    """Normalize a single type or a sequence of types into a tuple of types.

    Args:
        the_types (type or Sequence[type]): A type or sequence of types to normalize.

    Returns:
        Tuple[type, ...]: A tuple containing all provided types.

    Raises:
        TypeError: If any element in the input is not a type object.
    """
    if not isinstance(the_types, (list, tuple)):
        the_types = (the_types,)

    # Validate each item is a runtime 'type' (e.g., int, str, MyClass)
    for t in the_types:
        if not isinstance(t, type):
            raise TypeError(f"valid_types must be types; got {t!r}")

    return tuple(the_types)  # type: ignore[return-value]


class TypeValidationStrategy(ValidationStrategy[Any]):
    """Validation strategy to ensure the runtime "type" of a value is one of the allowed types.

    Args:
        valid_types (type or Sequence[type]): Allowed types for validation.
    """

    def __init__(self, valid_types: Sequence[type] | type):
        self.valid_types: Tuple[type, ...] = get_types(valid_types)

    def validate(self, value: Any) -> StatusResponse:
        """Validate that the value is of one of the allowed types.

        Args:
            value (Any): The value to validate.

        Returns:
            StatusResponse: Validation result with status and details.
        """
        if type(value) not in self.valid_types:
            types_str = ", ".join(f"'{t.__name__}'" for t in self.valid_types)
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be one of {types_str}, got '{type(value).__name__}'"
            )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)


class SameTypeValidationStrategy(ValidationStrategy[Any]):
    """Validation strategy to ensure two reference values have the same type.

    Args:
        value_a (Any): The first reference value.
        value_b (Any): The second reference value.
    """

    def __init__(self, value_a: Any, value_b: Any):
        self.value_a = value_a
        self.value_b = value_b

    def validate(self, value: Any) -> StatusResponse:
        """Validate that the two reference values have the same type.

        Args:
            value (Any): The value to validate (not used in type comparison).

        Returns:
            StatusResponse: Validation result with status and details.
        """
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
    """Validation strategy to ensure a value is within a specified range [low_value, high_value].

    Args:
        low_value (Any): The lower bound (inclusive).
        high_value (Any): The upper bound (inclusive).
    """

    def __init__(self, low_value: Any, high_value: Any):
        self.low_value = low_value
        self.high_value = high_value

    def validate(self, value: Any) -> StatusResponse:
        """Validate that the value is within the specified range.

        Args:
            value (Any): The value to validate.

        Returns:
            StatusResponse: Validation result with status and details.
        """
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
    """Validation strategy to ensure a value is one of a provided collection.

    Args:
        valid_values (Sequence[Any]): The collection of valid values.
    """

    def __init__(self, valid_values: Sequence[Any]):
        self.valid_values = valid_values

    def validate(self, value: Any) -> StatusResponse:
        """Validate that the value is in the collection of valid values.

        Args:
            value (Any): The value to validate.

        Returns:
            StatusResponse: Validation result with status and details.
        """
        if value not in self.valid_values:
            return StatusResponse(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_values}, got {value}"
            )
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)

class CoerceToType(TransformationStrategy[object, object]):
    """Transformation strategy to coerce a value to a target type (e.g., for range comparisons).

    Args:
        target_type (type): The type to coerce values to.

    Examples:
        int -> float
        int/float/str -> Decimal
        int/float -> Fraction

    Notes:
        - Converting float to Decimal can carry binary floating point artifacts; consider tightening if needed.
        - bool is a subclass of int; decide whether you want to accept it upstream.
    """
    __slots__ = ("_target_type",)

    def __init__(self, target_type: type):
        self._target_type = target_type

    def transform(self, value: object) -> Response[object]:
        """Coerce the value to the target type.

        Args:
            value (object): The value to coerce.

        Returns:
            Response[object]: The result of the coercion, with status and details.
        """
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
    """Validation strategy that always fails with a provided human-readable message.

    Args:
        details (str): The failure message to return.
    """
    __slots__ = ("_details",)

    def __init__(self, details: str):
        self._details = details

    def validate(self, value: Any) -> StatusResponse:
        """Always fail validation with the provided message.

        Args:
            value (Any): The value to validate (ignored).

        Returns:
            StatusResponse: Validation result with failure status and details.
        """
        return StatusResponse(status=Status.EXCEPTION, details=self._details)
