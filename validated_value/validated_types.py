from abc import ABC
from typing import List

from .value import ValidatedValue, ValidationStrategy
from .constants import DEFAULT_SUCCESS_MESSAGE
from .strategies import TypeValidationStrategy, EnumValidationStrategy, RangeValidationStrategy
from .response import T
from .status import Status

class EnumValidatedValue(ValidatedValue[T]):
    def get_strategies(self) -> List[ValidationStrategy]:
        return self._strategies

    def __init__(self, value, valid_types, valid_values, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        # Initialize the strategies for this subclass
        self._strategies = [
            TypeValidationStrategy(valid_types),
            EnumValidationStrategy(valid_values)
        ]
        super().__init__(value, success_details)


class RangeValidatedValue(ValidatedValue[T]):
    def get_strategies(self) -> List[ValidationStrategy]:
        return self._strategies

    def __init__(self, value, valid_types, low_value, high_value, success_details: str = DEFAULT_SUCCESS_MESSAGE):
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

    def __init__(self, value: T = None, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        super().__init__(value, success_details)
        if self.status == Status.EXCEPTION:
            raise ValueError(f"Validation failed for value '{value}': {self.details}")
