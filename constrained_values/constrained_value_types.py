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
    """Yield runtime types of values, de-duplicated in first-seen order."""
    seen: set[type] = set()
    for v in values:
        t = type(v)
        if t not in seen:
            seen.add(t)
            yield t


def types_of_values(values: Sequence[Any]) -> tuple[type, ...]:
    """
    Infer unique runtime types from values using a generator, then normalize via get_types(...).
    Kept as a tuple because get_types expects a concrete sequence (list/tuple).
    """
    return get_types(tuple(_iter_unique_types(values)))


class CoerceEnumMemberToValue(TransformationStrategy[object, object]):
    """If input is an Enum member, replace it with its .value; otherwise pass through."""

    def transform(self, value: object) -> Response[object]:
        if isinstance(value, Enum):
            return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value.value)
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


class ConstrainedEnumValue(ConstrainedValue[T]):
    """
    Validates enum-like values via a small pipeline:
      CoerceEnumMemberToValue                   # only when Enum class or enum members supplied
      TypeValidationStrategy(valid_types)       # exact runtime type(s) inferred from allowed values
      EnumValidationStrategy(allowed_values)    # membership check

    NOTE: No constructor-time exceptions for config mistakes. If the configuration
    is invalid (empty enum/sequence), we insert FailValidationStrategy so the
    instance surfaces status=EXCEPTION with a clear details message.
    """
    __slots__ = ("_strategies",)

    @classmethod
    def _all_enum_members(cls, seq: Sequence[Any]) -> bool:
        return len(seq) > 0 and all(isinstance(x, Enum) for x in seq)

    @classmethod
    def _normalize_allowed(cls, valid_values: Sequence[Any] | Type[Enum]) -> tuple[list[Any], bool, str | None]:
        """
        Normalize 'valid_values' into:
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
        if ConstrainedEnumValue._all_enum_members(seq):
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
        allowed, needs_coercion, err = ConstrainedEnumValue._normalize_allowed(valid_values)

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


class ConstrainedRangeValue(ConstrainedValue[T]):
    """
    A constrained numeric value bounded between ``low_value`` and ``high_value`` (inclusive).

    Pipeline structure
    ------------------
    The validation/transform pipeline is built in three parts:

      1. **Type strategies** (``_type_strategies``):
         - ``SameTypeValidationStrategy`` ensures the low/high bounds are of the same type.
         - ``TypeValidationStrategy`` infers acceptable input types from the bounds
           (e.g., float bounds → accept int and float; Decimal bounds → accept int/Decimal).
         - ``CoerceToType`` coerces the candidate into the type of ``low_value``.

      2. **Custom strategies** (from ``get_custom_strategies()``):
         - A hook for subclasses to inject additional transformations or validations.
         - Default implementation returns an empty list.
         - Example: converting Fahrenheit to Celsius before applying the range.

      3. **Range strategies** (``_range_strategies``):
         - ``RangeValidationStrategy`` enforces ``low_value <= value <= high_value``.

    Extension
    ---------
    To customize behavior, subclass and override ``get_custom_strategies()`

    Notes
    -----
    - Canonical values are always coerced to the type of ``low_value``.
    - If you pass bounds as floats, both int and float inputs are accepted
      and coerced to float.
    - If you pass bounds as Decimals, both int and Decimal inputs are accepted
      and coerced to Decimal.
    """
    __slots__ = ("_type_strategies","_range_strategies")

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
            TypeValidationStrategy(ConstrainedRangeValue.infer_valid_types_from_value(low_value)),
            CoerceToType(type(low_value))
        ])
        object.__setattr__(self, "_range_strategies", [
            RangeValidationStrategy(low_value, high_value)
        ])
        super().__init__(value, success_details)

"""
   StrictConstrainedValue Notes

   Python MRO (Method Resolution Order): 
   In Python, when a class inherits from multiple classes, 
   it follows an inheritance order defined by the C3 Linearization algorithm to determine which base class's 
   method to call. Essentially, it searches through each base class in the specified order until it finds 
   the method being called.
   
   Usage in StrictConstrainedValue
   
   class StrictMyClass(MyClass, StrictConstrainedValue):
   
   the MRO now starts with MyClass for the __init__() method:
    
   MyClass.__init__() is called first, which is designed to handle the argument (value) as expected.
   After MyClass is initialized, the MRO moves to StrictConstrainedValue. 
    
   The strict behavior in StrictConstrainedValue can then be applied after the basic validation has already happened.

   In essence, MyClass handles the initial validation logic, and StrictConstrainedValue adds the additional strict behavior (e.g., raising an exception).
   
"""


class StrictConstrainedValue(ConstrainedValue[T], ABC):
    """
    A stricter version of ConstrainedValue that raises an exception immediately if the validation fails.
    """
    def __init__(self, value: T = None, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        super().__init__(value, success_details)
        if self.status == Status.EXCEPTION:
            raise ValueError(f"Failed Constraints for value - '{value}': {self.details}")
