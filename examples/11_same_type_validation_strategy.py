"""Demonstrates strict same-type enforcement between two reference values
using :class:`SameTypeValidationStrategy`.

This example shows:
  * How two reference values are compared for exact type equality.
  * The strategy succeeds only if both reference types match exactly.
  * When types differ, the validation fails with `Status.EXCEPTION`.

Run directly:

    python examples/11_same_type_validation_strategy.py

Expected output:

    int vs int: OK
    int vs float: EXCEPTION
"""

import sys
import pathlib

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values.strategies import SameTypeValidationStrategy


def main() -> None:
    """Run the same-type validation demonstration.

    Creates two :class:`SameTypeValidationStrategy` instances:
      * One comparing `int` vs. `int` — should succeed.
      * One comparing `int` vs. `float` — should fail.

    Prints:
        * `"int vs int: OK"`
        * `"int vs float: EXCEPTION"`
    """
    print("int vs int:", SameTypeValidationStrategy(1, 2).validate("payload").status.name)
    print("int vs float:", SameTypeValidationStrategy(1, 2.0).validate(None).status.name)


if __name__ == "__main__":
    main()
