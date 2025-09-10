from abc import ABC, abstractmethod
from typing import Generic, List, Optional, Callable, Union
from .constants import DEFAULT_SUCCESS_MESSAGE
from .response import Response, T
from .status import Status
"""
Core value and validation abstractions.

- Value[T]: typed wrapper providing equality and ordering between *same-class* values.
- ValidationStrategy: pluggable unit that returns a Response (OK/EXCEPTION) and may transform the value.
- ValidatedValue[T]: Value that runs a sequence of strategies before exposing .value/.status/.details.
"""
class Value(Generic[T]):
    """
    A base class to represent a generic value. Provides comparison methods for equality, less than,
    and less than or equal to comparisons between instances of derived classes.
    """
    __slots__ = ("_value",)

    def __init__(self, value: T):
        self._value = value

    def _class_is_same(self, other) -> bool:
        return other.__class__ is self.__class__

    def __repr__(self):
        return f"{self.__class__.__name__}({self.value!r})"

    @property
    def value(self) -> T:
        """Returns the stored value."""
        return self._value

    def _compare(self, other: "Value[T]", comparison_func: Callable[[T, T], bool]) -> Union[bool, NotImplemented]:
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


class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, value) -> Response:
        """Perform validation and return a Response."""
        pass

class ValidatedValue(Value[T], ABC):
    """
    A Value that has been validated using a chain of ValidationStrategy objects.

    Each ValidatedValue wraps a raw `_value` and runs strategies in order.
    The outcome of validation is represented as a `Response`, which contains:
     - status: `Status.OK` if all strategies pass, else `Status.EXCEPTION`
     - details: a human-readable message from the failing strategy
     - value: the (possibly transformed) validated value, or None if invalid
    """
    def __repr__(self):
        return f"{self.__class__.__name__}(_value={self._value!r}, status={self.status.name})"

    __slots__ = ("_status", "_details")

    def __init__(self, value:T, success_details:str = DEFAULT_SUCCESS_MESSAGE):
        result = self._run_validations(value, success_details)
        super().__init__(result.value)
        self._status = result.status
        self._details = result.details

    def _run_validations(self, value, success_details:str)-> Response[T]:
        """
        Run validation strategies in order. If any returns EXCEPTION, short-circuit
        and propagate that Response. Otherwise, propagate the final (possibly transformed) value.
        """
        current_value = value  # Start with the initial value

        for strategy in tuple(self.get_strategies()):
            response = strategy.validate(current_value)
            if response.status == Status.EXCEPTION:
                return response  # Stop if any strategy fails
            # Update current_value with the value returned from the successful strategy
            current_value = response.value
        return Response(status=Status.OK, details=success_details, value=current_value)

    @abstractmethod
    def get_strategies(self) -> List[ValidationStrategy]:
        ...

    @property
    def status(self) -> Status:
        """Returns the status of the validation."""
        return self._status

    @property
    def details(self) -> str:
        """Returns the details of the validation status."""
        return self._details

    @property
    def value(self) -> Optional[T]:
        if self._status == Status.EXCEPTION:
            return None
        return self._value

    def _same_status(self, other):
        """Checks if another ValidatedValue instance has the same validation status."""
        return self.status == other.status

    def __eq__(self, other):
        if not self._class_is_same(other):
            return False
        if self.status != Status.OK or other.status != Status.OK:
            return False
        return super().__eq__(other)

    def _is_comparing(self, other: "ValidatedValue[T]",
                      func: Callable[["Value[T]"], Union[bool, NotImplemented]]):
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

