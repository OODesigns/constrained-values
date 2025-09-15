"""
Example 14 — ConstrainedEnumValue (sequence of enum members)
Supply members directly; input may be member or underlying.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from enum import Enum
from constrained_values import ConstrainedEnumValue


class Mixed(Enum):
    A = "a"
    B = "b"

def main():
    allowed = [Mixed.A, Mixed.B]
    x = ConstrainedEnumValue(Mixed.A, allowed)
    y = ConstrainedEnumValue("b", allowed)
    print("x:", x.status.name, x.value)
    print("y:", y.status.name, y.value)

if __name__ == "__main__":
    main()
