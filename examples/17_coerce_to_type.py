"""Demonstrates the use of :class:`CoerceToType` to normalize numeric types.

This example shows:
  * How integers can be coerced to floats.
  * How floats can be coerced to Decimals via string conversion.
  * How integers can be coerced to Fractions.
  * Each coercion returns a `Response` with `Status.OK` and a new, converted value.

Run directly:

    python examples/17_coerce_to_type.py

Expected output:

    int->float: 3.0
    float->Decimal: 0.1
    int->Fraction: 2
"""

import sys
import pathlib
from decimal import Decimal
from fractions import Fraction

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values.strategies import CoerceToType


def main() -> None:
    """Run the CoerceToType demonstration.

    Uses :class:`CoerceToType` to convert various numeric types.

    Steps:
        1. Coerce an integer to a `float`.
        2. Coerce a `float` to a `Decimal` (via string conversion).
        3. Coerce an integer to a `Fraction`.

    Prints:
        * `"int->float: 3.0"`
        * `"float->Decimal: 0.1"`
        * `"int->Fraction: 2"`
    """
    print("int->float:", CoerceToType(float).transform(3).value)
    print("float->Decimal:", CoerceToType(Decimal).transform(0.1).value)
    print("int->Fraction:", CoerceToType(Fraction).transform(2).value)


if __name__ == "__main__":
    main()
