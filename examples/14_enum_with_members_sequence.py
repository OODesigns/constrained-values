"""Demonstrates how :class:`EnumValue` can validate input against a sequence
of allowed Enum members instead of an Enum class.

This example shows:
  * How to supply a sequence of specific Enum members as valid options.
  * How input may be an Enum member or its underlying primitive value.
  * The `status` reports `Status.OK` when the input matches any allowed member.

Run directly:

    python examples/14_enum_with_members_sequence.py

Expected output:

    x: OK a
    y: OK b
"""

import sys
import pathlib
from enum import Enum

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import EnumValue


class Mixed(Enum):
    """A simple mixed-type enumeration."""
    A = "a"
    B = "b"


def main() -> None:
    """Run the EnumValue sequence demonstration.

    Creates two :class:`EnumValue` instances validated against a predefined
    list of allowed Enum members `[Mixed.A, Mixed.B]`.

    Steps:
        1. `EnumValue(Mixed.A, allowed)` — uses a valid Enum member directly.
        2. `EnumValue("b", allowed)` — uses the underlying value of an Enum
           member and still resolves successfully.

    Prints:
        * `"x: OK a"`
        * `"y: OK b"`
    """
    allowed = [Mixed.A, Mixed.B]
    x = EnumValue(Mixed.A, allowed)
    y = EnumValue("b", allowed)
    print("x:", x.status.name, x.value)
    print("y:", y.status.name, y.value)


if __name__ == "__main__":
    main()
