"""
Example 17 — CoerceToType
Numeric normalizations (int->float, float->Decimal via str, int->Fraction).
"""
from decimal import Decimal
from fractions import Fraction

from constrained_values.strategies import CoerceToType


def main():
    print("int->float:", CoerceToType(float).transform(3).value)
    print("float->Decimal:", CoerceToType(Decimal).transform(0.1).value)  # Decimal('0.1')
    print("int->Fraction:", CoerceToType(Fraction).transform(2).value)

if __name__ == "__main__":
    main()
