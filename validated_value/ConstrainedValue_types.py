from abc import ABC
from decimal import Decimal
from fractions import Fraction
from typing import List, Tuple, Type

from .value import ConstrainedValue, PipeLineStrategy
from .constants import DEFAULT_SUCCESS_MESSAGE
from .strategies import TypeValidationStrategy, EnumValidationStrategy, RangeValidationStrategy, \
    SameTypeValidationStrategy, CoerceToType
from .response import T
from .status import Status

class ConstrainedEnumValue(ConstrainedValue[T]):
    __slots__ = ("_strategies",)

    def get_strategies(self) -> List[PipeLineStrategy]:
        return self._strategies

    def __init__(self, value, valid_types, valid_values, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        # Initialize the strategies for this subclass
        object.__setattr__(self, "_strategies",[
            TypeValidationStrategy(valid_types),
            EnumValidationStrategy(valid_values)
        ])
        super().__init__(value, success_details)


class ConstrainedRangeValue(ConstrainedValue[T]):
    __slots__ = ("_strategies",)
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
        return self._strategies

    def __init__(self, value, low_value, high_value, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        # Initialize the strategies for this subclass
        object.__setattr__(self, "_strategies",[
            SameTypeValidationStrategy(low_value, high_value),
            TypeValidationStrategy(ConstrainedRangeValue.infer_valid_types_from_value(low_value)),
            CoerceToType(type(low_value)),
            RangeValidationStrategy(low_value, high_value)
        ])
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
class StrictValidatedValue(ConstrainedValue[T], ABC):
    """
    A stricter version of ValidatedValue that raises an exception immediately if the validation fails.
    """

    def __init__(self, value: T = None, success_details: str = DEFAULT_SUCCESS_MESSAGE):
        super().__init__(value, success_details)
        if self.status == Status.EXCEPTION:
            raise ValueError(f"Validation failed for value '{value}': {self.details}")
