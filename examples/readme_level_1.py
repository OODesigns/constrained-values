"""
Level 1: Simple Range Validation

The most basic use case is ensuring a value falls within a specific range. 
Instead of passing an integer around and checking its bounds everywhere, 
we create an `Age` type by defining a class.
"""
import sys, pathlib
from constrained_values import ConstrainedRangeValue

# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


def main():
    # Define an 'Age' type that must be an integer between 0 and 120.
    class Age(ConstrainedRangeValue[int]):
        def __init__(self, value):
            super().__init__(value, 0, 120)

    # Now, let's use our new Age type.
    valid_age = Age(30)
    invalid_age = Age(150)

    print(f"Valid age: {valid_age.value}, Is OK: {valid_age.ok}")
    # Output: Valid age: 30, Is OK: True

    print(f"Invalid age: {invalid_age.value}, Is OK: {invalid_age.ok}")
    # Output: Invalid age: None, Is OK: False

    print(f"Error details: {invalid_age.details}")
    # Output: Value must be less than or equal to 120, got 150


if __name__ == "__main__":
    main()
