from abc import ABC
from decimal import Decimal
from enum import Enum
from fractions import Fraction
from typing import List, Tuple, Type, TypeVar, Sequence, Any, Iterator

from .constants import DEFAULT_SUCCESS_MESSAGE
from .response import Response
from .status import Status
from .value import ConstrainedValue, PipeLineStrategy, TransformationStrategy
from .strategies import (
    TypeValidationStrategy,
    EnumValidationStrategy,
    RangeValidationStrategy,
    SameTypeValidationStrategy,
    CoerceToType,             # your numeric coercer used by ConstrainedRangeValue
    get_types,
    FailValidationStrategy,   # simple validation that returns EXCEPTION
)

T = TypeVar("T")

def _iter_unique_types(values: Sequence[Any]) -> Iterator[type]:
    """Yield unique runtime types of values in first-seen order.

    Args:
        values (Sequence[Any]): Sequence of values to infer types from.

    Yields:
        type: Unique types found in the input sequence.
    """
    seen: set[type] = set()
    for v in values:
        t = type(v)
        if t not in seen:
            seen.add(t)
            yield t


def types_of_values(values: Sequence[Any]) -> tuple[type, ...]:
    """Infer unique runtime types from values and normalize via get_types.

    Args:
        values (Sequence[Any]): Sequence of values to infer types from.

    Returns:
        tuple[type, ...]: Tuple of unique types found in the input sequence.
    """
    return get_types(tuple(_iter_unique_types(values)))


class CoerceEnumMemberToValue(TransformationStrategy[object, object]):
    """Transformation strategy that replaces Enum members with their .value, otherwise passes through.
    """
    def transform(self, value: object) -> Response[object]:
        """Transform the input value: if it is an Enum member, return its .value; otherwise, return the value unchanged.

        Args:
            value (object): The value to transform.

        Returns:
            Response[object]: Response containing the transformed value.
        """
        if isinstance(value, Enum):
            return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value.value)
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


class EnumValue(ConstrainedValue[T]):
    """Validates enum-like values using a pipeline of strategies.

    Pipeline:
        1. CoerceEnumMemberToValue: Converts Enum members to their values (if needed).
        2. TypeValidationStrategy: Ensures value is of allowed types.
        3. EnumValidationStrategy: Checks membership in allowed values.

    If configuration is invalid (e.g., empty enum/sequence), FailValidationStrategy is used to surface an error.

    Args:
        value (object): The value to validate.
        valid_values (Sequence[T] | Type[Enum]): Allowed values or Enum type.
        success_details (str, optional): Details for successful validation. Defaults to DEFAULT_SUCCESS_MESSAGE.

    Example:
        >>> EnumValue('A', ['A', 'B', 'C'])
    """
    __slots__ = ("_strategies",)

    @classmethod
    def _all_enum_members(cls, seq: Sequence[Any]) -> bool:
        return len(seq) > 0 and all(isinstance(x, Enum) for x in seq)

    @classmethod
    def _normalize_allowed(cls, valid_values: Sequence[Any] | Type[Enum]) -> tuple[list[Any], bool, str | None]:
        """Normalize 'valid_values' into:
          - allowed_values: list of canonical values to check membership against
          - needs_coercion: whether to add the enum→value coercion step
          - error_details: None if OK; otherwise a message explaining an error
        """
        seq = list(valid_values)

        # Enum class
        if isinstance(valid_values, type) and issubclass(valid_values, Enum):
            if not seq:
                return [], False, "Enum has no members."
            return [m.value for m in seq], True, None

        # Sequence
        if not seq:
            return [], False, "Must be a non-empty sequence."

        # Sequence of Enum members
        if EnumValue._all_enum_members(seq):
            return [m.value for m in seq], True, None

        # Plain values
        return seq, False, None

    def get_strategies(self) -> List[PipeLineStrategy]:
        return self._strategies

    def __init__(
            self,
            value: object,
            valid_values: Sequence[T] | Type[Enum],
            success_details: str = DEFAULT_SUCCESS_MESSAGE,
    ):
        allowed, needs_coercion, err = EnumValue._normalize_allowed(valid_values)

        strategies: List[PipeLineStrategy] = []
        if err is None:
            if needs_coercion:
                strategies.append(CoerceEnumMemberToValue())
            strategies += [
                TypeValidationStrategy(types_of_values(allowed)),
                EnumValidationStrategy(tuple(allowed)),
            ]
        else:
            # Config problem → report as EXCEPTION through the pipeline (no throws)
            strategies.append(FailValidationStrategy(err))

        object.__setattr__(self, "_strategies", strategies)
        super().__init__(value, success_details)


class RangeValue(ConstrainedValue[T]):
    """Constrained numeric value bounded between low_value and high_value (inclusive).

    Validation/transform pipeline:
        1. Type strategies:
            - SameTypeValidationStrategy: Ensures bounds are of the same type.
            - TypeValidationStrategy: Infers acceptable input types from bounds.
            - CoerceToType: Coerces candidate to type of low_value.
        2. Custom strategies: Hook for subclasses to inject additional logic.
        3. Range strategies:
            - RangeValidationStrategy: Enforces low_value <= value <= high_value.

    Args:
        value (Any): The value to validate.
        low_value (Any): Lower bound (inclusive).
        high_value (Any): Upper bound (inclusive).
        success_details (str, optional): Details for successful validation. Defaults to DEFAULT_SUCCESS_MESSAGE.

    Example:
        >>> RangeValue(5, 1, 10)

    Notes:
        - Canonical values are always coerced to the type of low_value.
        - If bounds are floats, both int and float inputs are accepted and coerced to float.
        - If bounds are Decimals, both int and Decimal inputs are accepted and coerced to Decimal.
    """
    __slots__ = ("_type_strategies", "_range_strategies")

    @classmethod
    def infer_valid_types_from_value(cls, value) -> Tuple[Type, ...]:
        t = type(value)
        if t is int:
            return (int,)
        if t is float:
            return int, float
        if t is Decimal:
            return int, Decimal
        if t is Fraction:
            return int, Fraction
        # default: exact type only
        return (t,)

    def get_strategies(self) -> List[PipeLineStrategy]:
        return self._type_strategies + self.get_custom_strategies() + self._range_strategies

    def get_custom_strategies(self) -> list[PipeLineStrategy]:
        return []

    def __init__(self, value, low_value, high_value, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        # Initialize the strategies for this subclass
        object.__setattr__(self, "_type_strategies", [
            SameTypeValidationStrategy(low_value, high_value),
            TypeValidationStrategy(RangeValue.infer_valid_types_from_value(low_value)),
            CoerceToType(type(low_value))
        ])
        object.__setattr__(self, "_range_strategies", [
            RangeValidationStrategy(low_value, high_value)
        ])
        super().__init__(value, success_details)



class StrictValue(ConstrainedValue[T], ABC):
    """Stricter version of ConstrainedValue that raises an exception immediately if validation fails.

    Args:
        value (T, optional): The value to validate. Defaults to None.
        success_details (str, optional): Details for successful validation. Defaults to DEFAULT_SUCCESS_MESSAGE.

    Raises:
        ValueError: If validation fails.
    """
    def __init__(self, value: T = None, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        super().__init__(value, success_details)
        if self.status == Status.EXCEPTION:
            raise ValueError(f"Failed Constraints for value - '{value}': {self.details}")
