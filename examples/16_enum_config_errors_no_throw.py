"""
Example 16 — ConstrainedEnumValue config errors
Empty enum / empty sequence → status=EXCEPTION (no exception thrown).
"""
from enum import Enum

from constrained_values import ConstrainedEnumValue


class Empty(Enum):
    pass

def main():
    a = ConstrainedEnumValue("anything", Empty)
    b = ConstrainedEnumValue("x", [])
    print("Empty Enum:", a.status.name, "-", a.details)
    print("Empty sequence:", b.status.name, "-", b.details)

if __name__ == "__main__":
    main()
