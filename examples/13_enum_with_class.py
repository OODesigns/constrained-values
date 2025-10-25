"""Demonstrates how :class:`EnumValue` handles inputs that are either Enum
members or their underlying primitive values.

This example shows:
  * How `EnumValue` accepts both an Enum member and its raw value.
  * The resulting canonical value is always the Enum member.
  * The `status` indicates successful validation in both cases.

Run directly:

    python examples/13_enum_with_class.py

Expected output:

    member → OK True
    underlying → OK True
"""

from enum import Enum
from constrained_values import EnumValue


class DataOrder(Enum):
    """A simple enumeration representing bit ordering."""
    MSB = True
    LSB = False


def main() -> None:
    """Run the EnumValue demonstration.

    Creates two :class:`EnumValue` instances:
      1. Using an Enum member directly (`DataOrder.MSB`).
      2. Using the underlying primitive value (`True`).

    Both inputs should resolve to the same Enum member and have
    `status = Status.OK`.

    Prints:
        * `"member → OK True"`
        * `"underlying → OK True"`
    """
    a = EnumValue(DataOrder.MSB, DataOrder)
    b = EnumValue(True, DataOrder)
    print("member →", a.status.name, a.value)
    print("underlying →", b.status.name, b.value)


if __name__ == "__main__":
    main()
