# Constrained Values

A Python library for creating type-safe, self-validating value objects using a powerful transformation and validation pipeline.

## The Philosophy: Beyond Primitive Types

In many applications, especially when interacting with hardware or external systems, we often pass around primitive types like integers, strings, or floats. This can lead to problems:

-   **Primitive Obsession:** Is `temperature = 25` in Celsius or Fahrenheit? Is `spi_mode = 2` a valid mode? Raw values lack context and safety.
-   **Lost Domain Knowledge:** The rules governing these values are scattered throughout the codebase. An `Age` shouldn't be negative, and a `Temperature` from a sensor might have a specific valid range.
-   **Bugs and Unreliability:** Passing an invalid value can lead to subtle bugs or crashes far from where the value was created.

The **Constrained Values** library solves this by embracing Object-Oriented principles. Instead of passing around a raw `int`, you create a rich, meaningful `Age` or `Temperature` object. This object encapsulates not just the value, but also the rules that govern it, ensuring that it can never exist in an invalid state.

This is particularly powerful for abstracting hardware domains. Instead of remembering that a [Modbus](https://www.modbus.org/) register value of `-32768` on a specific hardware means "no sensor detected," or that a valid Serial Peripheral Interface ([SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface#Original_definition)) "mode" is an integer between 0 and 3, you can create type-safe objects like `VentilationTemperature` or `SPIMode` that handle this complexity internally.

## Features

-   **Create Rich Value Objects:** Turn primitive data into meaningful, type-safe objects.
-   **Powerful Validation Pipelines:** Chain multiple validation and transformation steps.
-   **Built-in Strategies:** Includes common validators for ranges, enums, types, and more.
-   **Custom Logic:** Easily extend the library with your own validation and transformation strategies.
-   **Clear Error Handling:** Each constrained value clearly reports its status (`OK` or `EXCEPTION`) and provides descriptive error messages.
-   **Optional Error Throw:** When constructing a constrained value you can make it throw immediately, so you know an object is valid.    
-   **Type Safety:** Enforces the final, canonical type of your value.

## Installation

```bash
pip install constrained-values
```

## Progressive Examples

Let's explore the library's features, starting with a simple case and building up to a complex real-world scenario.

### Example 1: Simple Range Validation

The most basic use case is ensuring a value falls within a specific range. Instead of passing an integer around and checking its bounds everywhere, we create an `Age` type by defining a class.

```python
# See: examples/readme_example_1.py
# Define an 'Age' type that must be an integer between 0 and 120.
class Age(ConstrainedRangeValue[int]):
    def __init__(self, value):
        super().__init__(value, 0, 120)

# Now, let's use our new Age type.
valid_age = Age(30)
invalid_age = Age(150)
invalid_age_by_type = Age("21")
another_age = Age(32)

print(f"Valid age: {valid_age.value}, Is OK: {valid_age.ok}")
# Output: Valid age: 30, Is OK: True

print(f"Invalid age: {invalid_age.value}, Is OK: {invalid_age.ok}")
# Output: Invalid age: None, Is OK: False

print(f"Error details: {invalid_age.details}")
# Output: Value must be less than or equal to 120, got 150

print(f"Error details: {invalid_age_by_type.details}")
# Output: Error details: Value must be one of 'int', got 'str'

print(f"another_age: {another_age.value}, is greater than valid age: {valid_age.value} ? {another_age > valid_age}")
#Output: another_age: 32, is greater than valid age: 30 ? True

```
### Example 2: Using ConstrainedRangeValue with a custom transform (Fahrenheit → Celsius).

This demo shows how to subclass ConstrainedRangeValue and override
`get_custom_strategies()` to insert a transformation step into the pipeline.

- Input values are provided in Fahrenheit (int or float).
- A FahrenheitToCelsius transformation converts them to Celsius.
- The resulting Celsius values are validated against a range of -10°C .. 40°C.
- Results are rounded to two decimal places.

```python
# See: examples/readme_example_2.py
from constrained_values import Response, Status, ConstrainedRangeValue
from constrained_values.constants import DEFAULT_SUCCESS_MESSAGE
from constrained_values.value import TransformationStrategy

class FahrenheitToCelsius(TransformationStrategy[float, float]):
    """
    Define a transformation strategy for Fahrenheit.
    input and output types are float
    """
    def transform(self, value: float) -> Response[float]:
        try:
            c = round((float(value) - 32.0) * (5.0 / 9.0),2)
            return Response(Status.OK, DEFAULT_SUCCESS_MESSAGE, c)
        except Exception as e:
            return Response(Status.EXCEPTION, str(e), None)

class FahrenheitToCelsiusValue(ConstrainedRangeValue[float]):
    """
    Valid Celsius value between -10 and 40, inclusive.
    Accepts input as Fahrenheit (int/float).
    Fahrenheit is converted internally to Celsius before validation.
    """
    def __init__(self, value: int | float):
        super().__init__(value, -10.0, 40.0)

    def get_custom_strategies(self):
        return [FahrenheitToCelsius()]


print("\n=== Fahrenheit inputs (converted to Celsius) ===")
for val in [50, 50.36, 72]:
    cv = FahrenheitToCelsiusValue(val)
    print(f"Input {val!r}F → status={cv.status}, value={cv.value}°C")

print("\n=== Out of range examples ===")
for val in [-40, 10, 122]:
    cv = FahrenheitToCelsiusValue(val)
    print(f"Input {val!r} → status={cv.status}, details={cv.details}")
```
### Level 3: Complex Pipelines for Hardware Data

This is where the library truly shines. Let's model a real-world hardware scenario: reading a temperature from a **ventilation unit via the [Modbus](https://www.modbus.org/) protocol**.

The process involves multiple steps:
1.  The input is a register address (an `int`).
2.  We must validate that we are allowed to read from this register.
3.  We fetch the raw integer value from a list of all Modbus registers.
4.  The hardware uses special values (`-32768`, `32767`) to signal errors like a missing or short-circuited sensor. We must detect these.
5.  If the value is valid, it's not yet in Celsius. We need to divide it by `10.0` to get the final temperature.

Here’s how you can model this entire chain of validation and transformation using a custom `ConstrainedRangeValue`.

```python
from typing import List
from constrained_values import (Response, Status, ConstrainedRangeValue,
                                ValidationStrategy, TypeValidationStrategy, DEFAULT_SUCCESS_MESSAGE)
from constrained_values.response import StatusResponse
from constrained_values.value import TransformationStrategy, PipeLineStrategy

# --- Define Custom Strategies for our Pipeline ---
class AllowedInputRegister(ValidationStrategy[int]):
    """Checks if the selected register address is valid."""

    def validate(self, value: int) -> StatusResponse:
        valid_registers = {0, 1, 2, 3}
        if value in valid_registers:
            return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)
        return StatusResponse(status=Status.EXCEPTION, details="Invalid temperature register selected")


class GetValueFromRegister(TransformationStrategy[int, int]):
    """Fetches the raw integer from the Modbus data list."""

    def __init__(self, input_register: List[int]):
        self.input_register = input_register

    def transform(self, value: int) -> Response[int]:
        raw_sensor_value = self.input_register[value]
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=raw_sensor_value)


class DetectSensorErrors(ValidationStrategy[int]):
    """Checks for hardware-specific error codes."""
    NO_SENSOR = -32768
    SENSOR_SHORT = 32767

    def validate(self, value: int) -> StatusResponse:
        if value == self.NO_SENSOR:
            return StatusResponse(status=Status.EXCEPTION, details="No sensor detected")
        if value == self.SENSOR_SHORT:
            return StatusResponse(status=Status.EXCEPTION, details="Sensor short circuit")
        return StatusResponse(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE)


class RawToCelsius(TransformationStrategy[int, float]):
    """Transforms the raw integer to a float in degrees Celsius."""

    def transform(self, value: int) -> Response[float]:
        celsius = float(value) / 10.0
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=celsius)


class VentilationTemperature(ConstrainedRangeValue[float]):
    """
    This value object encapsulates the full pipeline of reading and validating
    temperature data from Modbus (https://www.modbus.org/) input registers, converting to Celsius, and
    enforcing an allowed range.
    """
    __slots__ = ("_getValueFromRegister",)

    def __init__(self, input_register: Response[int], selected_register: int):
        object.__setattr__(self, "_getValueFromRegister", GetValueFromRegister(input_register))
        super().__init__(selected_register, -10.0, 40.0)

    def get_strategies(self) -> List[PipeLineStrategy]:
        return [TypeValidationStrategy(int),
                AllowedInputRegister(),
                self._getValueFromRegister,
                DetectSensorErrors(),
                RawToCelsius()] + super().get_strategies()


    -- Test Cases --        
    registers = [215, -32768, 32767, 402]  # Example Modbus register values

    print("=== Valid register 0 ===")
    v = VentilationTemperature(registers, 0)
    print(f"status={v.status}, details={v.details}, value={v.value}")  # → 21.5°C
    # Output # status=Status.OK, details=validation successful, value=21.5

    print("\n=== Invalid: No sensor detected (register 1) ===")
    v = VentilationTemperature(registers, 1)
    print(f"status={v.status}, details={v.details}")
    # Output # status=Status.EXCEPTION, details=No sensor detected

    print("\n=== Invalid: Sensor short circuit (register 2) ===")
    v = VentilationTemperature(registers, 2)
    print(f"status={v.status}, details={v.details}")
    # Output # status=Status.EXCEPTION, details=Sensor short circuit

    print("\n=== Out of range (register 3) ===")
    v = VentilationTemperature(registers, 3)
    print(f"status={v.status}, details={v.details}")
    # Output # status=Status.EXCEPTION, details=Value must be less than or equal to 40.0, got 40.2
```

This example demonstrates how `constrained-values` can tame complexity by creating a clean, reliable interface over messy, real-world data.

## Further Examples

For more examples, please see the [`examples/`](./examples) directory, which includes:
- Chained transformations (`09_chained_transforms.py`)
- Type coercion and validation (`10_type_validation_strategy.py`, `17_coerce_to_type.py`)
- Enum validation (`13_enum_with_class.py`)
- And many more.

