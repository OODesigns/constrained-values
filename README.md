# Constrained Values

A Python library for creating value objects that are constrained by validation rules.

This library provides a `ConstrainedValue` class that can be used to create value objects with built-in validation. It's useful for ensuring that data conforms to specific constraints at the point of creation, making your code more robust and reliable.

## Features

-   Create value objects with validation rules.
-   Support for various validation strategies (e.g., range, enum, type coercion).
-   Clear separation of valid and invalid values.
-   Easy to extend with custom validation logic.
-   Provides a `response` object to inspect validation results.

## Installation

```bash
pip install constrained-values
```

## Usage

Here's a simple example of how to create a constrained value:

```python
from constrained_values import ConstrainedValue
from constrained_values.strategies import Range

# Create a constrained integer between 1 and 100
Age = ConstrainedValue(int, Range(1, 100))

# Create a valid age
valid_age = Age(25)
print(f"Valid age: {valid_age.value}, is_ok: {valid_age.is_ok()}")  # Output: Valid age: 25, is_ok: True

# Create an invalid age
invalid_age = Age(150)
print(f"Invalid age: {invalid_age.value}, is_ok: {invalid_age.is_ok()}")  # Output: Invalid age: 150, is_ok: False
print(f"Error: {invalid_age.error_message()}") # Output: Error: 150 is not within the range 1-100
```
