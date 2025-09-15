# Constrained Values

A Python library for creating type-safe, self-validating value objects using powerful transformation and validation pipelines.

## The Philosophy: Beyond Primitive Types

In many applications, especially when interacting with hardware or external systems, we often pass around primitive types like integers, strings, or floats. This can lead to problems:

-   **Primitive Obsession:** Is `temperature = 25` in Celsius or Fahrenheit? Is `spi_mode = 2` a valid mode? Raw values lack context and safety.
-   **Lost Domain Knowledge:** The rules governing these values are scattered throughout the codebase. An `Age` shouldn't be negative, and a `Temperature` from a sensor might have a specific valid range.
-   **Bugs and Unreliability:** Passing an invalid value can lead to subtle bugs or crashes far from where the value was created.

The **Constrained Values** library solves this by embracing Object-Oriented principles. Instead of passing around a raw `int`, you create a rich, meaningful `Age` or `Temperature` object. This object encapsulates not just the value, but also the rules that govern it, ensuring that it can never exist in an invalid state.

This is particularly powerful for abstracting hardware domains. Instead of remembering that a Modbus register value of `-32768` means "no sensor detected," or that a valid SPI mode is an integer between 0 and 3, you can create type-safe objects like `BlaubergTemperature` or `SPIMode` that handle this complexity internally.

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

### Level 1: Simple Range Validation

The most basic use case is ensuring a value falls within a specific range. Instead of passing an integer around and checking its bounds everywhere, we create an `Age` type by defining a class.

```python
# See: examples/03_constrained_pass_through.py
from typing import List
from constrained_values import ConstrainedValue
from constrained_values.strategies import Range, PipeLineStrategy

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

```

We can do the same for a `Temperature` object.

```python
from typing import List
from constrained_values import ConstrainedValue
from constrained_values.strategies import Range, PipeLineStrategy

# A temperature valid for a specific sensor, in Celsius.
class SensorTemperature(ConstrainedValue[float]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [Range(-40.0, 85.0)]

good_temp = SensorTemperature(25.5)
bad_temp = SensorTemperature(100.0)

print(f"Good temperature: {good_temp.value}°C, Is OK: {good_temp.ok}")
# Output: Good temperature: 25.5°C, Is OK: True

print(f"Bad temperature: {bad_temp.value}°C, Is OK: {bad_temp.ok}")
# Output: Bad temperature: None, Is OK: False
```

### Level 2: Abstracting Hardware Constants

When working with hardware, you often deal with "magic numbers." For example, SPI (Serial Peripheral Interface) has a "mode" that must be 0, 1, 2, or 3. Forgetting this leads to bugs.

Let's create an `SPIMode` object to make our code self-documenting and safe.

```python
# See: examples/13_enum_with_class.py
from constrained_values import ConstrainedValue
from constrained_values.strategies import Range

# Instead of remembering the range 0-3, we encode it in the type.
SPIMode = ConstrainedValue.factory(int, [Range(0, 3)])

# Now, using it is clear and safe.
mode_1 = SPIMode(1)
invalid_mode = SPIMode(5)

print(f"SPI Mode: {mode_1.value}, Is OK: {mode_1.ok}")
# Output: SPI Mode: 1, Is OK: True

print(f"Invalid SPI Mode: {invalid_mode.details}")
# Output: Invalid SPI Mode: 5 is not within the range 0-3
```
By using `SPIMode(1)` instead of the raw integer `1`, you make your function signatures and code far more readable and prevent a whole class of errors.

### Level 3: Complex Pipelines for Hardware Data

This is where the library truly shines. Let's model a real-world hardware scenario: reading a temperature from a **Blauberg ventilation unit via Modbus**.

The process involves multiple steps:
1.  The input is a register address (an `int`).
2.  We must validate that we are allowed to read from this register.
3.  We fetch the raw integer value from a list of all Modbus registers.
4.  The hardware uses special values (`-32768`, `32767`) to signal errors like a missing or short-circuited sensor. We must detect these.
5.  If the value is valid, it's not yet in Celsius. We need to divide it by `10.0` to get the final temperature.

Here’s how you can model this entire chain of validation and transformation using a custom `ConstrainedValue`.

```python
# This is a conceptual example based on the attached blauberg_temperature.py
from typing import List
from constrained_values import ConstrainedValue, Response, Status
from constrained_values.strategies import (
    ValidationStrategy,
    TransformationStrategy,
    Range,
)

# --- Define Custom Strategies for our Pipeline ---

class AllowedInputRegister(ValidationStrategy):
    """Checks if the selected register address is valid."""
    def validate(self, value: int) -> Response:
        valid_registers = {0, 1, 2, 3} # Example addresses
        if value in valid_registers:
            return Response(status=Status.OK, value=value)
        return Response(status=Status.EXCEPTION, details="Invalid temperature register selected")

class GetValueFromModbus(TransformationStrategy):
    """Fetches the raw integer from the Modbus data list."""
    def __init__(self, modbus_data: List[int]):
        self.modbus_data = modbus_data

    def transform(self, value: int) -> Response:
        raw_sensor_value = self.modbus_data[value]
        return Response(status=Status.OK, value=raw_sensor_value)

class DetectSensorErrors(ValidationStrategy):
    """Checks for hardware-specific error codes."""
    NO_SENSOR = -32768
    SENSOR_SHORT = 32767
    def validate(self, value: int) -> Response:
        if value == self.NO_SENSOR:
            return Response(status=Status.EXCEPTION, details="No sensor detected")
        if value == self.SENSOR_SHORT:
            return Response(status=Status.EXCEPTION, details="Sensor short circuit")
        return Response(status=Status.OK, value=value)

class RawToCelsius(TransformationStrategy):
    """Transforms the raw integer to a float in degrees Celsius."""
    def transform(self, value: int) -> Response:
        celsius = float(value) / 10.0
        return Response(status=Status.OK, value=celsius)

# --- Create the ConstrainedValue Factory ---

def get_blauberg_temp_factory(modbus_data: List[int]):
    """This factory builds our complex temperature object."""
    return ConstrainedValue.factory(
        final_type=float,
        strategies=[
            AllowedInputRegister(),
            GetValueFromModbus(modbus_data),
            DetectSensorErrors(),
            RawToCelsius(),
            Range(-40.0, 85.0), # Finally, validate the Celsius range
        ]
    )

# --- Usage ---

# Simulate the data read from the Modbus device
live_modbus_registers = [250, 195, -32768, 500] # Raw values for 4 registers

# Get our factory
BlaubergTemperature = get_blauberg_temp_factory(live_modbus_registers)

# --- Test Cases ---

# 1. Read a valid temperature from register 0
temp1 = BlaubergTemperature(0) # Input is the register address
print(f"Temp 1: {temp1.value}°C, OK: {temp1.ok}")
# Output: Temp 1: 25.0°C, OK: True

# 2. Try to read from a register with a sensor error
temp2 = BlaubergTemperature(2)
print(f"Temp 2: {temp2.value}, OK: {temp2.ok}, Details: {temp2.details}")
# Output: Temp 2: None, OK: False, Details: No sensor detected

# 3. Try to read from a register that is out of the final valid range
temp3 = BlaubergTemperature(3) # 500 / 10.0 = 50.0, which is valid
print(f"Temp 3: {temp3.value}°C, OK: {temp3.ok}")
# Output: Temp 3: 50.0°C, OK: True

# 4. Try to read from a disallowed register
temp4 = BlaubergTemperature(10)
print(f"Temp 4: {temp4.value}, OK: {temp4.ok}, Details: {temp4.details}")
# Output: Temp 4: None, OK: False, Details: Invalid temperature register selected
```

This example demonstrates how `constrained-values` can tame complexity by creating a clean, reliable interface over messy, real-world data.

## Further Examples

For more examples, please see the [`examples/`](./examples) directory, which includes:
- Chained transformations (`09_chained_transforms.py`)
- Type coercion and validation (`10_type_validation_strategy.py`, `17_coerce_to_type.py`)
- Enum validation (`13_enum_with_class.py`)
- And many more.

