"""
Example 11 — SameTypeValidationStrategy
Strict same-type enforcement for two reference values.
"""
from constrained_values.strategies import SameTypeValidationStrategy


def main():
    print("int vs int:", SameTypeValidationStrategy(1, 2).validate("payload").status.name)
    print("int vs float:", SameTypeValidationStrategy(1, 2.0).validate(None).status.name)

if __name__ == "__main__":
    main()
