A Python library for creating type-safe, self-validating value objects using a powerful transformation and validation pipeline.

## The Philosophy: Beyond Primitive Types

In many applications, especially when interacting with hardware or external systems, we often pass around primitive types like integers, strings, or floats. This can lead to problems:

-   **Primitive Obsession:** Is `temperature = 25` in Celsius or Fahrenheit? Is `spi_mode = 2` a valid mode? Raw values lack context and safety.
-   **Lost Domain Knowledge:** The rules governing these values are scattered throughout the codebase. An `Age` shouldn't be negative, and a `Temperature` from a sensor might have a specific valid range.
-   **Bugs and Unreliability:** Passing an invalid value can lead to subtle bugs or crashes far from where the value was created.

The **Constrained Values** library solves this by embracing Object-Oriented principles. Instead of passing around a raw `int`, you create a rich, meaningful `Age` or `Temperature` object. This object encapsulates not just the value, but also the rules that govern it, ensuring that it can never exist in an invalid state.

This is particularly powerful for abstracting hardware domains. Instead of remembering that a [Modbus](https://www.modbus.org/) (Ventilation Comms) register value of `-32768` on a specific hardware means "no sensor detected," or that a valid Serial Peripheral Interface ([SPI](https://en.wikipedia.org/wiki/Serial_Peripheral_Interface#Original_definition)) "mode" is an integer between 0 and 3, you can create type-safe objects like `VentilationTemperature` or `SPIMode` that handle this complexity internally.

## Features

-   **Create Rich Value Objects:** Turn primitive data into meaningful, type-safe objects.
-   **Powerful Validation Pipelines:** Chain multiple validation and transformation steps.
-   **Built-in Strategies:** Includes common validators for ranges, enums, types, and more.
-   **Custom Logic:** Easily extend the library with your own validation and transformation strategies.
-   **Clear Error Handling:** Each constrained value clearly reports its status (`OK` or `EXCEPTION`) and provides descriptive error messages.
-   **Optional Error Throw:** When constructing a constrained value you can make it throw immediately, so you know an object is valid.
-   **Type Safety:** Enforces the final, canonical type of your value.

## Typed, Pipeline-Driven Value Objects

This module provides a small set of primitives for building typed, pipeline-driven value objects:

- **`Value[T]`** — An immutable, typed wrapper that defines equality and ordering  
  *only against the same concrete subclass.*

- **`ValidationStrategy`** — A pluggable check that returns a `StatusResponse`  
  (`Status.OK` or `Status.EXCEPTION`) without changing the value.

- **`TransformationStrategy`** — A pluggable step that converts an input value of type `Generic[InT]` to  
  a new value and returns a `Response[OutT]` (status, details, value).

- **`ConstrainedValue[T]`** — A value object that runs an input through a sequence  
  of strategies (transformations and validations) to produce a canonical `T`,  
  plus status and details.

## Typical Flow

1. Start from a raw input (which may not yet be of type `T`).
2. Thread it through a pipeline: transformations may change the value or type,  
   while validations only inspect it.
3. On the first `Status.EXCEPTION`, the pipeline short-circuits. Otherwise,  
   the final value is accepted and exposed as the canonical `T`.

---
## Quickstart

## Progressive Examples

Let's explore the library's features, starting with a simple case and building up to a complex real-world scenario.

### Example 1: Simple Range Validation

The most basic use case is ensuring a value falls within a specific range. Instead of passing an integer around and checking its bounds everywhere, we create an `Age` type by defining a class.

```python
# See: examples/readme_example_1.py
# Define an 'Age' type that must be an integer between 0 and 120.
class Age(RangeValue[int]):
    def __init__(self, value):
        super().__init__(value, 10, 120)

    # Now, let's use our new Age type.
    valid_age = Age(30)
    invalid_age = Age(150)
    invalid_age_by_type = Age("21")
    another_valid_age = Age(32)

    print(
        f"Another valid age: {another_valid_age.value}, "
        f"is greater than valid age: {valid_age.value} ? "
        f"{another_valid_age > valid_age}"
    )
    print(f"Valid age: {valid_age.value}, Is OK: {valid_age.ok}")
    print(f"Invalid age: {invalid_age.value}, Is OK: {invalid_age.ok}")
    print(f"Error details: {invalid_age.details}")
    print(f"Error details: {invalid_age_by_type.details}")
```
Output
```console
Another valid age: 32, is greater than valid age: 30 ? True
Valid age: 30, Is OK: True
Invalid age: None, Is OK: False
Error details: Value must be less than or equal to 120, got 150
Error details: Value must be one of 'int', got 'str'
```