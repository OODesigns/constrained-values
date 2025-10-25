"""Demonstrates that ordering comparisons (`<`, `>`, etc.) between
different subclasses of :class:`ConstrainedValue` are not supported.

This example shows:
  * Each subclass (`A`, `B`) defines its own validation strategy.
  * Ordering between **instances of the same class** works normally.
  * Ordering between **different subclasses** raises a `TypeError`.

Run directly:

    python examples/21_cross_class_ordering_type_error.py

Expected output:

    TypeError (as designed): '<' not supported between instances of 'A' and 'B'
"""

import sys
import pathlib
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Pass(TransformationStrategy[int, int]):
    """A transformation strategy that passes through integer values."""

    def transform(self, value: int) -> Response[int]:
        """Return a successful response with the input unchanged.

        Args:
            value: The integer to pass through.

        Returns:
            Response[int]: Contains:
                * `status = Status.OK`
                * `details = "ok"`
                * `value` equal to the input
        """
        return Response(status=Status.OK, details="ok", value=value)


class A(ConstrainedValue[int]):
    """A simple `ConstrainedValue` subclass using the `Pass` strategy."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step successful pipeline."""
        return [Pass()]


class B(ConstrainedValue[int]):
    """Another `ConstrainedValue` subclass using the same `Pass` strategy.

    This class intentionally mirrors `A`, but cross-class ordering comparisons
    (`A < B` or `B > A`) are designed to fail with `TypeError`.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step successful pipeline."""
        return [Pass()]


def main() -> None:
    """Run the cross-class ordering demonstration.

    Creates two constrained values from different subclasses (`A` and `B`) and
    attempts to compare them using the `<` operator.
    Since ordering is only defined between instances of the *same subclass*,
    a `TypeError` is raised.

    Prints:
        * `"TypeError (as designed): '<' not supported between instances of 'A' and 'B'"`
    """
    a, b = A(1), B(2)
    try:
        print("a < b →", a < b)
    except TypeError as e:
        print("TypeError (as designed):", e)


if __name__ == "__main__":
    main()
