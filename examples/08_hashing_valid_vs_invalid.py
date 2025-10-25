"""Demonstrates how valid and invalid `ConstrainedValue` instances behave when
hashed or used in sets and equality comparisons.

This example shows:
  * Valid values hash based on their **(class, value)** pair.
  * Invalid values hash based on their **(class, status)** pair.
  * Equal valid instances collapse to one entry in a set.
  * Invalid instances remain distinct, even if their input data is identical.

Run directly:

    python examples/08_hashing_valid_vs_invalid.py

Expected output:

    equal valid hashes: True
    set size for valid duplicates (1): 1
    invalid equal? (False): False
    both hashable: True
    set size for invalid values (2): 2
"""

import sys
import pathlib
from typing import Any

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue


class Pass(TransformationStrategy[Any, Any]):
    """A transformation strategy that always succeeds.

    Produces an `OK` response and returns the input value unchanged.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return an OK response with the input value.

        Args:
            value: The input to pass through unchanged.

        Returns:
            Response[Any]: A successful response containing:
                * `status = Status.OK`
                * `details = "ok"`
                * `value` equal to the input
        """
        return Response(status=Status.OK, details="ok", value=value)


class Fail(TransformationStrategy[Any, Any]):
    """A transformation strategy that always fails.

    Used to demonstrate how failed constrained values behave when hashed.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return a failed response.

        Args:
            value: Any input value (ignored).

        Returns:
            Response[Any]: A failed response containing:
                * `status = Status.EXCEPTION`
                * `details = "boom"`
                * `value = None`
        """
        return Response(status=Status.EXCEPTION, details="boom", value=None)


class ValidInt(ConstrainedValue[int]):
    """A valid constrained integer that always succeeds.

    Uses a single `Pass` strategy.
    """

    def get_strategies(self):
        """Return a one-step pass-through pipeline."""
        return [Pass()]


class InvalidInt(ConstrainedValue[int]):
    """An invalid constrained integer that always fails.

    Uses a single `Fail` strategy to simulate validation failure.
    """

    def get_strategies(self):
        """Return a one-step failing pipeline."""
        return [Fail()]


def main() -> None:
    """Run the hashing comparison demonstration.

    Steps:
        1. Create two valid constrained values (`a`, `b`) with identical input.
        2. Show that they have equal hashes and collapse in a set.
        3. Create two invalid constrained values (`x`, `y`) and show that
           they are not equal, but remain hashable and distinct in sets.

    Prints:
        * Whether the hashes of valid values are equal (`True`)
        * The set size for valid duplicates (`1`)
        * Equality result for invalid values (`False`)
        * Confirmation that invalid values are still hashable (`True`)
        * The set size for invalid values (`2`)
    """
    a, b = ValidInt(42), ValidInt(42)
    print("equal valid hashes:", hash(a) == hash(b))
    s = {a, b}
    print("set size for valid duplicates (1):", len(s))

    x, y = InvalidInt(1), InvalidInt(1)
    print("invalid equal? (False):", x == y)
    print("both hashable:", isinstance(hash(x), int) and isinstance(hash(y), int))
    s2 = {x, y}
    print("set size for invalid values (2):", len(s2))


if __name__ == "__main__":
    main()
