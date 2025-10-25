"""Demonstrates how to enforce runtime type validation using
:class:`TypeValidationStrategy`.

This example shows:
  * How to create a `TypeValidationStrategy` that accepts multiple types.
  * How `.validate()` returns an OK or EXCEPTION `Response` based on type match.
  * How to inspect the returned status and details fields.

Run directly:

    python examples/10_type_validation_strategy.py

Expected output:

    validate 3: OK
    validate 3.0: OK
    validate 'x': EXCEPTION - Value must be one of 'int', 'float', got 'str'
"""

import sys
import pathlib

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import TypeValidationStrategy


def main() -> None:
    """Run the type validation demonstration.

    Creates a :class:`TypeValidationStrategy` that allows `int` and `float`
    values, then validates several inputs to show how the strategy enforces
    runtime type checks.

    Steps:
        1. Validate `3` (int) → passes.
        2. Validate `3.0` (float) → passes.
        3. Validate `'x'` (str) → fails with EXCEPTION.

    Prints:
        * `"validate 3: OK"`
        * `"validate 3.0: OK"`
        * `"validate 'x': EXCEPTION - Value must be one of 'int', 'float', got 'str'"`
    """
    s = TypeValidationStrategy([int, float])
    print("validate 3:", s.validate(3).status.name)
    print("validate 3.0:", s.validate(3.0).status.name)
    r = s.validate("x")
    print("validate 'x':", r.status.name, "-", r.details)


if __name__ == "__main__":
    main()
