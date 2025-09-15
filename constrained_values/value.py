"""
Core value and validation abstractions.

- Value[T]: typed wrapper providing equality and ordering between *same-class* values.
- ValidationStrategy: pluggable unit that returns a StatusResponse (OK/EXCEPTION).
- TransformationStrategy: pluggable unit that transforms and returns a Response[OutT].
- ConstrainedValue: runs a sequence of strategies on a raw input (which may differ from the final T) before exposing .value/.status/.details.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from types import NotImplementedType
from typing import Generic, List, Optional, Callable, TypeVar, Any
from .constants import DEFAULT_SUCCESS_MESSAGE
from .response import Response, StatusResponse
from .status import Status
T = TypeVar("T")        # final canonical type

@dataclass(frozen=True, slots=True)
class Value(Generic[T]):
    """
    A base class to represent a generic immutable value.

    Immutability & memory:
      - Implemented via dataclass(frozen=True) which prevents attribute mutation after __init__.
      - slots=True avoids per-instance __dict__ and disallows arbitrary attributes.

    Equality & ordering:
      - Equality compares *same-class* values on the underlying data.
      - Ordering is only defined between the same concrete class.
    """
    # Stored payload; immutable thanks to frozen dataclass
    _value: T

    def _class_is_same(self, other) -> bool:
        return other.__class__ is self.__class__

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    @property
    def value(self) -> T:
        """Returns the stored value."""
        return self._value

    def _compare(self, other: "Value[T]", comparison_func: Callable[[T, T], bool]) -> bool | NotImplementedType:
        if self._class_is_same(other):
            return comparison_func(self.value, other.value)
        return NotImplemented

    def __eq__(self, other):
        return self._compare(other, lambda x, y: x == y)

    def __lt__(self, other):
        res = self._compare(other, lambda x, y: x < y)
        return NotImplemented if res is NotImplemented else res

    def __le__(self, other):
        res = self._compare(other, lambda x, y: x <= y)
        return NotImplemented if res is NotImplemented else res

    def __gt__(self, other):
        res = self._compare(other, lambda x, y: x > y)
        return NotImplemented if res is NotImplemented else res

    def __ge__(self, other):
        res = self._compare(other, lambda x, y: x >= y)
        return NotImplemented if res is NotImplemented else res

    def __hash__(self):
        return hash((self.__class__, self._value))

    def __str__(self) -> str:
        return str(self.value)

    def __format__(self, format_spec: str) -> str:
        # Delegate formatting to the underlying value
        return format(self.value, format_spec)

InT = TypeVar("InT")    # raw input type
MidT = TypeVar("MidT")  # intermediate type(s) in the pipeline
OutT = TypeVar("OutT")  # output of a single transform step

class PipeLineStrategy(ABC):
    """Marker base for pipeline steps (either ValidationStrategy or TransformationStrategy)."""
    pass

class ValidationStrategy(Generic[MidT], PipeLineStrategy):
    @abstractmethod
    def validate(self, value: MidT) -> StatusResponse: # pragma: no cover
        """Perform validation and return a StatusResponse."""
        pass

class TransformationStrategy(Generic[InT, OutT], PipeLineStrategy):
    @abstractmethod
    def transform(self, value: InT) -> Response[OutT]: # pragma: no cover
        """Transform the value and return a Response[OutT]."""
        pass

class ConstrainedValue(Value[T], ABC):
    """

    A value processed by a pipeline of transformation and validation strategies.

    Each instance accepts a raw `value_in` (which may not yet be of the final type `T`)
    and runs a series of strategies in order to produce a canonical value and status.

    These strategies can either transform the value (e.g., sanitize, clean, or convert it into a canonical form)
    or validate it against specific rules.

    The outcome of the pipeline is represented as a Response, which contains:
     - status: Status.OK if all strategies pass, else Status.EXCEPTION
     - details: a human-readable message from the failing strategy
     - value: the final, transformed and validated value, or None if the process fails.

    Equality & ordering:
      - Two instances are equal only if they are the same concrete class AND both are valid (Status.OK) AND their underlying values are equal.
      - Ordering comparisons raise if either side is invalid.

    Truthiness:
      - bool(x) is True if status == Status.OK (see .ok).

    Hashing:
      - Valid instances hash by (class, value); invalid instances hash by (class, status).
        This keeps invalids distinct from valid instances but may cluster many invalids in one bucket.

    Raises:
      - ValueError: when calling unwrap() on an invalid instance (status != Status.OK).
     """
    def __repr__(self):
        return f"{self.__class__.__name__}(_value={self._value!r}, status={self.status.name})"

    __slots__ = ("_status", "_details")

    def __init__(self, value_in: InT, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        result = self._run_pipeline(value_in, success_details)
        super().__init__(result.value)
        object.__setattr__(self, "_status", result.status)
        object.__setattr__(self, "_details", result.details)

    @classmethod
    def _apply_strategy(cls, strategy: PipeLineStrategy, current_value: Any) -> Response[Any]:
        """
        Run a single pipeline strategy and normalize the result to a Response[Any].
        - For transformations: return the strategy's Response.
        - For validations: wrap the StatusResponse into a Response carrying current_value.
        """
        if isinstance(strategy, TransformationStrategy):
            return strategy.transform(current_value)
        elif isinstance(strategy, ValidationStrategy):
            # ValidationStrategy: keep the current value unchanged
            sr = strategy.validate(current_value)
            return Response(status=sr.status, details=sr.details, value=current_value)
        return Response(status=Status.EXCEPTION, details="Missing strategy handler", value=None)

    def _run_pipeline(self, value_in: InT, success_details:str)-> Response[T]:
        """
        The current value is threaded through the pipeline; transformation steps may change its
        type (e.g., sanitize or convert), and validation steps check the current value without
        changing it. On the first EXCEPTION status, the pipeline short-circuits and returns that
        failure response; otherwise, it returns OK with the final canonical value.
        """
        current_value = value_in  # Start with the initial value

        for strategy in self.get_strategies():
            resp = self._apply_strategy(strategy, current_value)
            if resp.status == Status.EXCEPTION:
                return Response(status=Status.EXCEPTION, details=resp.details, value=None)
            # OK → thread the (possibly transformed) value
            current_value = resp.value

        return Response(status=Status.OK, details=success_details, value=current_value)

    @abstractmethod
    def get_strategies(self) -> List[PipeLineStrategy]:
        ...

    @property
    def status(self) -> Status:
        return self._status

    @property
    def details(self) -> str:
        return self._details

    @property
    def value(self) -> Optional[T]:
        if self._status == Status.EXCEPTION:
            return None
        return self._value

    def _same_status(self, other):
        return self.status == other.status

    def __eq__(self, other):
        if not self._class_is_same(other):
            return False
        if self.status != Status.OK or other.status != Status.OK:
            return False
        return super().__eq__(other)

    def _is_comparing(self, other: "ConstrainedValue[T]",
                      func: Callable[["Value[T]"], bool | NotImplementedType]):
        """
        Internal helper for ordering comparisons:
        - Ensures same concrete class
        - Ensures both operands are valid (Status.OK)
        - Delegates to the base Value comparator
        """
        if not self._class_is_same(other):
            return NotImplemented
        if self.status != Status.OK or other.status != Status.OK:
            raise ValueError(f"{self.__class__.__name__}: cannot compare invalid values")
        return func(other)

    def __lt__(self, other):
        return self._is_comparing(other, super().__lt__)

    def __le__(self, other):
        return self._is_comparing(other, super().__le__)

    def __gt__(self, other):
        return self._is_comparing(other, super().__gt__)

    def __ge__(self, other):
        return self._is_comparing(other, super().__ge__)

    def __hash__(self):
        if self.status == Status.OK:
            # Match value-based equality for valid instances
            return hash((self.__class__, self._value))
        # For invalid instances: still hashable, but distinct from any valid instance
        # Don’t include .details (too volatile); status is enough.
        return hash((self.__class__, self.status))

    def __bool__(self) -> bool:
        return self.status == Status.OK

    def __str__(self) -> str:
        # Print the canonical value when valid; show a concise marker when invalid
        return str(self._value) if self.status == Status.OK else f"<invalid {self.__class__.__name__}: {self.details}>"

    # Ensures invalid values format to the same marker as __str__ (not "None").
    # This keeps f-strings readable even when the instance is invalid.
    def __format__(self, format_spec: str) -> str:
        if self.status == Status.OK:
            return format(self._value, format_spec)
        return str(self)

    def unwrap(self) -> T:
        """Return the validated value or raise if invalid (ergonomic for callers)."""
        if self.status != Status.OK:
            raise ValueError(f"{self.__class__.__name__} invalid: {self.details}")
        return self._value

    @property
    def ok(self) -> bool:
        """Convenience alias for status == Status.OK."""
        return self.status == Status.OK




