"""
Example: Using RangeValue with a custom transform (Fahrenheit → Celsius).

This demo shows how to subclass RangeValue and override
`get_custom_strategies()` to insert a transformation step into the pipeline.

- Input values are provided in Fahrenheit (int or float).
- A FahrenheitToCelsius transformation converts them to Celsius.
- The resulting Celsius values are validated against a range of -10°C .. 40°C.
- Results are rounded to two decimal places.
"""
import sys, pathlib
from constrained_values import Response, Status, RangeValue
from constrained_values.constants import DEFAULT_SUCCESS_MESSAGE
from constrained_values.value import TransformationStrategy

# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

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


class FahrenheitToCelsiusValue(RangeValue[float]):
    """
    Valid Celsius value between -10 and 40, inclusive.
    Accepts input as Fahrenheit (int/float).
    Fahrenheit is converted internally to Celsius before validation.
    """
    def __init__(self, value: int | float):
        super().__init__(value, -10.0, 40.0)

    def get_custom_strategies(self):
         return [FahrenheitToCelsius()]

def main():
    print("\n=== Fahrenheit inputs (converted to Celsius) ===")
    for val in [50, 50.36, 72]:
        cv = FahrenheitToCelsiusValue(val)
        print(f"Input {val!r}F → status={cv.status}, value={cv.value}°C")

    print("\n=== Out of range examples ===")
    for val in [-40, 10, 122]:
        cv = FahrenheitToCelsiusValue(val)
        print(f"Input {val!r} → status={cv.status}, \n details={cv.details}")

if __name__ == "__main__":
    main()