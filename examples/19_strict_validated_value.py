"""Demonstrates how :class:`StrictValue` differs from regular
:class:`ConstrainedValue` by raising exceptions instead of returning
a non-OK status when validation fails.

This example shows:
  * How `StrictValue` automatically validates in its constructor.
  * That a successful pipeline behaves like `ConstrainedValue`.
  * That a failing pipeline raises `ValueError` immediately.

Run directly:

    python examples/19_strict_validated_value.py

Expected output:

    AlwaysOK: OK 7
    AlwaysFail raised: Failed Constraints for value - '9': boom
"""

import sys
import pathlib
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import StrictValue
from constrained_values.strategies import FailValidationStrategy


class AlwaysOK(StrictValue[int]):
    """A `StrictValue[int]` that always succeeds.

    Since it defines no failing strategies, all values pass validation.
    """

    def get_strategies(self) -> List:
        """Return an empty strategy list."""
        return []


class AlwaysFail(StrictValue[int]):
    """A `StrictValue[int]` that always fails.

    The strategy list contains a single :class:`FailValidationStrategy`,
    which raises a `ValueError` when validation runs.
    """

    def get_strategies(self) -> List:
        """Return a single failing strategy."""
        return [FailValidationStrategy("boom")]


def main() -> None:
    """Run the StrictValue demonstration.

    Creates two subclasses of :class:`StrictValue`:

      1. **AlwaysOK** — accepts any input successfully.
      2. **AlwaysFail** — raises a `ValueError` during initialization.

    Prints:
        * `"AlwaysOK: OK 7"`
        * `"AlwaysFail raised: Failed Constraints for value - '9': boom"`
    """
    x = AlwaysOK(7)
    print("AlwaysOK:", x.status.name, x.value)

    try:
        AlwaysFail(9)
    except ValueError as e:
        print("AlwaysFail raised:", e)


if __name__ == "__main__":
    main()
