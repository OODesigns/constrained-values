"""
Constrained value representing a validated ventilation temperature in Celsius.

Pipeline stages
---------------
The pipeline processes input in multiple steps:

1. **TypeValidationStrategy(int)**
   Ensure the register selector is an integer.

2. **AllowedInputRegister**
   Ensure the chosen register index is one of the supported registers {0, 1, 2, 3}.

3. **GetValueFromRegister**
   Fetch the raw sensor value from the provided Modbus input register list.

4. **DetectSensorErrors**
   Check for hardware error codes:
     - -32768 → "No sensor detected"
     -  32767 → "Sensor short circuit"

5. **RawToCelsius**
   Convert the raw integer to Celsius by dividing by 10.0.

6. **Parent pipeline (ConstrainedRangeValue)**
   - Type normalization (float)
   - Coercion to type of `low_value` (`float`)
   - Range validation (-10.0 .. 40.0 °C)
"""
import sys, pathlib
from typing import List
from constrained_values import (Response, Status, ConstrainedRangeValue,
                                ValidationStrategy, TypeValidationStrategy, DEFAULT_SUCCESS_MESSAGE)
from constrained_values.response import StatusResponse
from constrained_values.value import TransformationStrategy, PipeLineStrategy

# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))


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
    Valid Celsius value between -10 and 40, inclusive.
    Accepts input as Fahrenheit (int/float).
    Fahrenheit is converted internally to Celsius before validation.
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


def main():
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


if __name__ == "__main__":
    main()
