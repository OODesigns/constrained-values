"""
Example 13 — ConstrainedEnumValue (Enum class input)
Accept both enum members and their underlying values.
"""

from enum import Enum

from constrained_values import EnumValue


class DataOrder(Enum):
    MSB = True
    LSB = False

def main():
    a = EnumValue(DataOrder.MSB, DataOrder)
    b = EnumValue(True, DataOrder)
    print("member →", a.status.name, a.value)
    print("underlying →", b.status.name, b.value)

if __name__ == "__main__":
    main()
