from abc import ABC, abstractmethod
from typing import Generic, List, Optional

from .constants import DEFAULT_SUCCESS_MESSAGE
from .response import Response, T
from .status import Status

class Value(Generic[T]):
    """
    A base class to represent a generic value. Provides comparison methods for equality, less than,
    and less than or equal to comparisons between instances of derived classes.
    """
    __slots__ = ("_value",)

    def __init__(self, value: T):
        self._value = value

    @property
    def value(self) -> T:
        """Returns the stored value."""
        return self._value

    def _compare(self, other, comparison_func):
        if other.__class__ is self.__class__:
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


class ValidationStrategy(ABC):
    @abstractmethod
    def validate(self, value) -> Response:
        """Perform validation and return a Response."""
        pass

class ValidatedValue(Value[T], ABC):
    """
    A base class that represents a value which must be validated. ValidationStrategy are required to implement
    the validate method to perform validation and return a ValidatedResult.

    Attributes:
        _status: The status of the validation.
        _details: Additional details regarding the validation status.
    """

    def __init__(self, value:T, success_details:str = DEFAULT_SUCCESS_MESSAGE):
        result = self._run_validations(value, success_details)
        super().__init__(result.value)
        self._status = result.status
        self._details = result.details

    def _run_validations(self, value, success_details:str):
        """Run the list of validation strategies on the value, chaining responses.
        :value:
        :success_details: description the success details of the validation
        """
        current_value = value  # Start with the initial value

        for strategy in self.get_strategies():
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
        """Checks equality considering both validation status and value."""
        return self._same_status(other) and super().__eq__(other)

    def __lt__(self, other):
        """Checks if this value is less than another, considering validation status."""
        return self._same_status(other) and super().__lt__(other)

    def __le__(self, other):
        """Checks if this value is less than or equal to another, considering validation status."""
        return self._same_status(other) and super().__le__(other)


