"""Demonstrates how :class:`RangeValue` automatically coerces the input type
to match the type of its range bounds.

This example shows:
  * When both bounds are `float`, an `int` input is coerced to `float`.
  * When both bounds are `Decimal`, the input is converted to `Decimal`.
  * When both bounds are `Fraction`, the input is converted to `Fraction`.

Run directly:

    python examples/12_range_with_coercion.py

Expected output:

    int->float: 3.0
    int->Decimal: 3
    int->Fraction: 1
"""

import sys
import pathlib
from decimal import Decimal
from fractions import Fraction

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import RangeValue


def main() -> None:
    """Run the range coercion demonstration.

    Creates three :class:`RangeValue` instances with different numeric bound
    types to demonstrate automatic coercion of the input value.

    Steps:
        1. Input `3` coerced to `float` because bounds are `0.0` and `10.0`.
        2. Input `3` coerced to `Decimal` because bounds are Decimal objects.
        3. Input `1` coerced to `Fraction` because bounds are Fractions.

    Prints:
        * `"int->float: 3.0"`
        * `"int->Decimal: 3"`
        * `"int->Fraction: 1"`
    """
    print("int->float:", RangeValue(3, 0.0, 10.0).value)
    print("int->Decimal:", RangeValue(3, Decimal("0"), Decimal("10")).value)
    print("int->Fraction:", RangeValue(1, Fraction(0, 1), Fraction(3, 2)).value)


if __name__ == "__main__":
    main()
