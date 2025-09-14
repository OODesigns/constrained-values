"""
Example 15 — ConstrainedEnumValue (plain values)
Allowed values as plain list/tuple.
"""
from constrained_values import ConstrainedEnumValue


def main():
    ok = ConstrainedEnumValue("a", ["a", "b"])
    bad = ConstrainedEnumValue("c", ["a", "b"])
    print("ok:", ok.status.name, ok.value)
    print("bad:", bad.status.name, bad.details)

if __name__ == "__main__":
    main()
