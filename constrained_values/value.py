"""Core value and validation abstractions.

This module provides a small set of primitives for building typed, pipeline-driven
value objects:

- ``Value[T]``: An immutable, typed wrapper that defines equality and ordering
  **only against the same concrete subclass**.
- ``ValidationStrategy``: A pluggable check that returns a ``StatusResponse``
  (``Status.OK`` or ``Status.EXCEPTION``) without changing the value.
- ``TransformationStrategy``: A pluggable step that converts an input value to
  a new value and returns a ``Response[OutT]`` (status, details, value).
- ``ConstrainedValue[T]``: A value object that runs an input through a sequence
  of strategies (transformations and validations) to produce a canonical ``T``,
  plus status and details.

Typical flow
------------
1) Start from a raw input (which may not be type ``T`` yet).
2) Thread it through a pipeline: transformations may change the value/type,
   validations only inspect it.
3) On the first ``Status.EXCEPTION`` the pipeline short-circuits; otherwise,
   the final value is accepted and exposed as the canonical ``T``.
"""
from __future__ import annotations
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
    """Immutable, typed value wrapper with same-class comparison semantics.

    A lightweight wrapper around a value of type ``T``. Instances compare for
    equality and ordering **only** against the same concrete subclass; cross-class
    comparisons return ``NotImplemented`` (so Python can try reversed ops).

    The dataclass is ``frozen=True`` for immutability and uses ``__slots__`` to
    reduce memory footprint.

    Type Variables:
        T: The canonical type of the wrapped value.

    Attributes:
        _value (T): The wrapped value (read-only).
    """

    # Stored payload; immutable thanks to frozen dataclass
    _value: T

    def _class_is_same(self, other) -> bool:
        """Return True if `other` is the same concrete subclass as `self`."""
        return other.__class__ is self.__class__

    def __repr__(self):
        """Use !r to ensure the underlying value is shown with its repr() form
        (developer-friendly and unambiguous, e.g., Value('foo') instead of Value(foo)).
        """
        return f"{self.__class__.__name__}({self.value!r})"

    @property
    def value(self) -> T:
        """Returns the stored value."""
        return self._value

    def _compare(self, other: Value[T], comparison_func: Callable[[T, T], bool]) -> bool | NotImplementedType:
        """Compare values using the provided function if classes match.

        Args:
            other (Value[T]): The other value instance to compare.
            comparison_func (Callable[[T, T], bool]): The comparator used when classes match.

        Returns:
            bool | NotImplementedType: Result of the comparison or NotImplemented for cross-class.
        """
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
    """Abstract base for pipeline processing strategies.

    Marker class for steps in a :class:`ConstrainedValue` pipeline. Concrete
    subclasses implement either validation or transformation behaviour.
    """
    pass

class ValidationStrategy(Generic[MidT], PipeLineStrategy):
    """Abstract base class for validation strategies.

    Subclasses should implement :meth:`validate` to examine the provided value
    and return a :class:`~constrained_values.response.StatusResponse` describing
    whether the value is valid.

    Type variables:
        MidT: The type of value accepted by this validator.
    """

    @abstractmethod
    def validate(self, value: MidT) -> StatusResponse:  # pragma: no cover
        """Validate ``value`` and return a StatusResponse.

        Args:
            value (MidT): Value to validate.

        Returns:
            StatusResponse: Validation outcome (status and details).
        """
        pass

class TransformationStrategy(Generic[InT, OutT], PipeLineStrategy):
    """Abstract base class for transformation strategies.

    Subclasses should implement :meth:`transform` to convert a value from
    ``InT`` to ``OutT`` and return a :class:`~constrained_values.response.Response`.

    Type variables:
        InT: Input type accepted by this transformer.
        OutT: Output type produced by this transformer.
    """

    @abstractmethod
    def transform(self, value: InT) -> Response[OutT]:  # pragma: no cover
        """Transform ``value`` and return a Response.

        Args:
            value (InT): Input value to transform.

        Returns:
            Response[OutT]: The transformed value with status and details.
        """
        pass

class ConstrainedValue(Value[T], ABC):
    """A value that is validated/transformed by a processing pipeline.

    A :class:`ConstrainedValue` accepts raw input (``InT``) and runs it through a
    configured sequence of :class:`PipeLineStrategy` steps (transformations and
    validations) to produce a canonical value of type ``T`` and a validation
    status.

    Type Variables:
        T: The canonical (final) type after pipeline processing.
        InT: The raw input type supplied to the constructor.

    Private Attributes:
        _status (Status): Current status (OK or EXCEPTION).
        _details (str): Human-readable details about the validation / transformation result.

    Properties:
        value (Optional[T]): The canonical value if valid, else ``None``.
        ok (bool): True when status is OK.

    Raises:
        ValueError: When calling :meth:`unwrap` on an invalid instance.
    """
    def __repr__(self):
        """Developer-friendly representation including value and status."""
        return f"{self.__class__.__name__}(_value={self._value!r}, status={self.status.name})"

    __slots__ = ("_status", "_details")

    def __init__(self, value_in: InT, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        result = self._run_pipeline(value_in, success_details)
        super().__init__(result.value)
        object.__setattr__(self, "_status", result.status)
        object.__setattr__(self, "_details", result.details)

    @classmethod
    def _apply_strategy(cls, strategy: PipeLineStrategy, current_value: Any) -> Response[Any]:
        """Run a single pipeline strategy and normalize the result.

        Behavior:
            - For transformations: return the strategy's Response.
            - For validations: wrap the StatusResponse into a Response that carries the current value unchanged.

        Args:
            strategy (PipeLineStrategy): The pipeline strategy to apply.
            current_value (Any): The current value being threaded through the pipeline.

        Returns:
            Response[Any]: A normalized response containing status, details, and value.
        """
        if isinstance(strategy, TransformationStrategy):
            return strategy.transform(current_value)
        elif isinstance(strategy, ValidationStrategy):
            # ValidationStrategy: keep the current value unchanged
            sr = strategy.validate(current_value)
            return Response(status=sr.status, details=sr.details, value=current_value)
        return Response(status=Status.EXCEPTION, details="Missing strategy handler", value=None)

    def _run_pipeline(self, value_in: InT, success_details:str)-> Response[T]:
        """Thread the current value through the configured pipeline.

        Transformation steps may change the value (or type), while validation steps only
        inspect it. On the first ``Status.EXCEPTION`` the pipeline short-circuits and
        returns that failure response; otherwise, it returns OK with the final canonical value.

        Args:
            value_in (InT): The raw input value to start the pipeline.
            success_details (str): Details message to use when the pipeline completes with OK.

        Returns:
            Response[T]: The terminal response (status, details, and canonical value).
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
        """Return the ordered list of strategies for this pipeline.

        Returns:
            List[PipeLineStrategy]: Transformation and validation steps in the order to apply.
        """
        ...
    @property
    def status(self) -> Status:
        """Current status (OK or EXCEPTION)."""
        return self._status

    @property
    def details(self) -> str:
        """Human-readable details about the validation / transformation result."""
        return self._details

    @property
    def value(self) -> Optional[T]:
        """Canonical value if valid; otherwise ``None`` when status is EXCEPTION."""
        if self._status == Status.EXCEPTION:
            return None
        return self._value

    def _same_status(self, other):
        """Return True if both instances share the same Status."""
        return self.status == other.status

    def __eq__(self, other):
        if not self._class_is_same(other):
            return False
        if self.status != Status.OK or other.status != Status.OK:
            return False
        return super().__eq__(other)

    def _is_comparing(self, other: ConstrainedValue[T],
                  func: Callable[[Value[T]], bool | NotImplementedType]):
        """Perform a comparison with another ConstrainedValue instance.

        Internal helper for ordering comparisons:
        - Ensures the same concrete subclass.
        - Ensures both operands are valid (Status.OK).
        - Delegates the comparison to the base Value comparator.

        Args:
            other (ConstrainedValue[T]): The other instance to compare against.
            func (Callable[[Value[T]], bool | NotImplementedType]): The comparison
                function to delegate to (e.g., ``super().__lt__``).

        Returns:
            bool | NotImplementedType: The result of the comparison if valid, or
            ``NotImplemented`` if the instances are not comparable.

        Raises:
            ValueError: If either operand has a non-OK validation status.
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




