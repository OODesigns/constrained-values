"""Demonstrates how multiple transformation steps can be chained together
before final validation within a `ConstrainedValue` pipeline.

This example shows:
  * How multiple `TransformationStrategy` instances operate sequentially.
  * How each step modifies the intermediate value.
  * How a `RangeValidationStrategy` validates the final result.
  * How success and failure propagate through the pipeline.

Run directly:

    python examples/09_chained_transforms.py

Expected output:

    ok: OK 10
    bad: EXCEPTION Value must be less than or equal to 50, got 54 None
"""

import sys
import pathlib
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, RangeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Inc(TransformationStrategy[int, int]):
    """A transformation strategy that increments the value by one."""

    def transform(self, value: int) -> Response[int]:
        """Increment the given value.

        Args:
            value: The integer to increment.

        Returns:
            Response[int]: Contains:
                * `status = Status.OK`
                * `details = "inc"`
                * `value = value + 1`
        """
        return Response(status=Status.OK, details="inc", value=value + 1)


class Double(TransformationStrategy[int, int]):
    """A transformation strategy that doubles the input value."""

    def transform(self, value: int) -> Response[int]:
        """Multiply the value by two.

        Args:
            value: The integer to double.

        Returns:
            Response[int]: Contains:
                * `status = Status.OK`
                * `details = "double"`
                * `value = value * 2`
        """
        return Response(status=Status.OK, details="double", value=value * 2)


class Chained(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that chains multiple transformation steps.

    The transformation pipeline:
        1. `Inc()` – adds 1.
        2. `Double()` – multiplies by 2.
        3. `RangeValidationStrategy(10, 50)` – ensures the final value is within range.

    This shows how complex constraints can be composed using multiple
    reusable strategies.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the chained transformation and validation pipeline."""
        return [Inc(), Double(), RangeValidationStrategy(10, 50)]


def main() -> None:
    """Run the chained transformation demonstration.

    Creates two `Chained` constrained values:
      * One with input `4` → (4 + 1) * 2 = 10 → OK.
      * One with input `26` → (26 + 1) * 2 = 54 → out of range → EXCEPTION.

    Prints:
        * `"ok: OK 10"`
        * `"bad: EXCEPTION Value must be less than or equal to 50, got 54 None"`
    """
    ok = Chained(4)    # (4+1)*2 = 10 → OK
    bad = Chained(26)  # (26+1)*2 = 54 → out of range
    print("ok:", ok.status.name, ok.value)
    print("bad:", bad.status.name, bad.details, bad.value)


if __name__ == "__main__":
    main()
