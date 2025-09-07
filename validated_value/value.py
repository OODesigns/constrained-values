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


class TypeValidationStrategy(ValidationStrategy):
    def __init__(self, valid_types):
        # If valid_types is a single type, convert it to a tuple
        if not isinstance(valid_types, (list, tuple)):
            valid_types = (valid_types,)
        self.valid_types = tuple(valid_types)  # Ensure it's always a tuple

    def validate(self, value) -> Response:
        if not isinstance(value, self.valid_types):
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_types}, got {type(value).__name__}",
                value=None
            )
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


class RangeValidationStrategy(ValidationStrategy):
    def __init__(self, low_value, high_value):
        self.low_value = low_value
        self.high_value = high_value

    def validate(self, value) -> Response:
        if value < self.low_value:
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be greater than or equal to {self.low_value}, got {value}",
                value=None
            )
        if value > self.high_value:
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be less than or equal to {self.high_value}, got {value}",
                value=None
            )
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


class EnumValidationStrategy(ValidationStrategy):
    def __init__(self, valid_values):
        self.valid_values = valid_values

    def validate(self, value) -> Response:
        if value not in self.valid_values:
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_values}, got {value}",
                value=None
            )
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


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


class EnumValidatedValue(ValidatedValue[T]):
    def get_strategies(self) -> List[ValidationStrategy]:
        return self._strategies

    def __init__(self, value, valid_types, valid_values, success_details:str = DEFAULT_SUCCESS_MESSAGE):
        # Initialize the strategies for this subclass
        self._strategies = [
            TypeValidationStrategy(valid_types),
            EnumValidationStrategy(valid_values)
        ]
        super().__init__(value, success_details)


class RangeValidatedValue(ValidatedValue[T]):
    def get_strategies(self) -> List[ValidationStrategy]:
        return self._strategies

    def __init__(self, value, valid_types, low_value, high_value, success_details:str = DEFAULT_SUCCESS_MESSAGE):
        # Initialize the strategies for this subclass
        self._strategies = [
            TypeValidationStrategy(valid_types),
            RangeValidationStrategy(low_value, high_value)
        ]
        super().__init__(value, success_details)


"""
   StrictValidatedValue Notes

   Python MRO (Method Resolution Order): 
   In Python, when a class inherits from multiple classes, 
   it follows an inheritance order defined by the C3 Linearization algorithm to determine which base class's 
   method to call. Essentially, it searches through each base class in the specified order until it finds 
   the method being called.
   
   Usage in StrictValidatedValue
   
   class StrictMyClass(MyClass, StrictValidatedValue):
   
   the MRO now starts with MyClass for the __init__() method:
    
   MyClass.__init__() is called first, which is designed to handle the argument (value) as expected.
   After MyClass is initialized, the MRO moves to StrictValidatedValue. 
    
   The strict behavior in StrictValidatedValue can then be applied after the basic validation has already happened.

   In essence, MyClass handles the initial validation logic, and StrictValidatedValue adds the additional strict behavior (e.g., raising an exception).
   
"""

class StrictValidatedValue(ValidatedValue[T], ABC):
    """
    A stricter version of ValidatedValue that raises an exception immediately if the validation fails.
    """
    def __init__(self, value: T = None, success_details:str = DEFAULT_SUCCESS_MESSAGE):
        super().__init__(value, success_details)
        if self.status == Status.EXCEPTION:
            raise ValueError(f"Validation failed for value '{value}': {self.details}")