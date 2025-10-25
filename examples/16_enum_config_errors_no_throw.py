"""Demonstrates how :class:`EnumValue` handles configuration errors gracefully
by reporting `Status.EXCEPTION` rather than throwing runtime exceptions.

This example shows:
  * Behavior when an `EnumValue` is initialized with an empty Enum class.
  * Behavior when an `EnumValue` is initialized with an empty allowed sequence.
  * In both cases, `status = EXCEPTION` and a descriptive error message
    appears in `details`.

Run directly:

    python examples/16_enum_config_errors_no_throw.py

Expected output:

    Empty Enum: EXCEPTION - Enum has no members.
    Empty sequence: EXCEPTION - Must be a non-empty sequence.
"""

import sys
import pathlib
from enum import Enum

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import EnumValue


class Empty(Enum):
    """An empty enumeration with no members."""
    pass


def main() -> None:
    """Run the EnumValue configuration error demonstration.

    Creates two misconfigured :class:`EnumValue` instances to show how
    invalid configurations are handled without raising exceptions.

    Steps:
        1. Instantiate `EnumValue("anything", Empty)` → empty Enum class.
        2. Instantiate `EnumValue("x", [])` → empty allowed value sequence.

    Both cases produce `status = Status.EXCEPTION`, and error details
    are provided via the `.details` field.

    Prints:
        * `"Empty Enum: EXCEPTION - Enum has no members."`
        * `"Empty sequence: EXCEPTION - Must be a non-empty sequence."`
    """
    a = EnumValue("anything", Empty)
    b = EnumValue("x", [])
    print("Empty Enum:", a.status.name, "-", a.details)
    print("Empty sequence:", b.status.name, "-", b.details)


if __name__ == "__main__":
    main()
