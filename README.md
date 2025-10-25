# Constrained Values

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

## Installation

```bash
pip install constrained-values
```

Creating Docs... please wait...

## Examples
For examples, please see the [`examples/`](./examples) directory, which includes:
- Chained transformations (`09_chained_transforms.py`)
- Type coercion and validation (`10_type_validation_strategy.py`, `17_coerce_to_type.py`)
- Enum validation (`13_enum_with_class.py`)
- And many more.

