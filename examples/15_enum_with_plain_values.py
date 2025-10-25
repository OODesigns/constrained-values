"""Demonstrates how :class:`EnumValue` can be constructed from a plain list or
tuple of allowed values (not an Enum class or Enum members).

This example shows:
  * How to define a simple allowed value set as a list of primitives.
  * How validation passes when the input is in the allowed list.
  * How validation fails when the input is not in the allowed list.

Run directly:

    python examples/15_enum_with_plain_values.py

Expected output:

    ok: OK a
    bad: EXCEPTION Value must be one of ('a', 'b'), got c
"""

import sys
import pathlib

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import EnumValue


def main() -> None:
    """Run the EnumValue plain-value demonstration.

    Creates two :class:`EnumValue` instances with a list of plain string
    values `["a", "b"]` as the allowed set.

    Steps:
        1. `EnumValue("a", ["a", "b"])` → passes validation (OK).
        2. `EnumValue("c", ["a", "b"])` → fails validation (EXCEPTION).

    Prints:
        * `"ok: OK a"`
        * `"bad: EXCEPTION Value must be one of ('a', 'b'), got c"`
    """
    ok = EnumValue("a", ["a", "b"])
    bad = EnumValue("c", ["a", "b"])
    print("ok:", ok.status.name, ok.value)
    print("bad:", bad.status.name, bad.details)


if __name__ == "__main__":
    main()
