"""
Example 12 — ConstrainedRangeValue with coercion
int coerced to float/Decimal/Fraction based on bound type.
"""
from decimal import Decimal
from fractions import Fraction

from constrained_values import ConstrainedRangeValue


def main():
    print("int->float:", ConstrainedRangeValue(3, 0.0, 10.0).value)
    print("int->Decimal:", ConstrainedRangeValue(3, Decimal("0"), Decimal("10")).value)
    print("int->Fraction:", ConstrainedRangeValue(1, Fraction(0,1), Fraction(3,2)).value)

if __name__ == "__main__":
    main()
