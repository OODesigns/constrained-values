"""
Example 10 — TypeValidationStrategy
Enforcing exact runtime types.
"""
from constrained_values import TypeValidationStrategy


def main():
    s = TypeValidationStrategy([int, float])
    print("validate 3:", s.validate(3).status.name)
    print("validate 3.0:", s.validate(3.0).status.name)
    r = s.validate("x")
    print("validate 'x':", r.status.name, "-", r.details)

if __name__ == "__main__":
    main()
