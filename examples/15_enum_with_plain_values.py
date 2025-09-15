"""
Example 15 — ConstrainedEnumValue (plain values)
Allowed values as plain list/tuple.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from constrained_values import ConstrainedEnumValue

def main():
    ok = ConstrainedEnumValue("a", ["a", "b"])
    bad = ConstrainedEnumValue("c", ["a", "b"])
    print("ok:", ok.status.name, ok.value)
    print("bad:", bad.status.name, bad.details)

if __name__ == "__main__":
    main()
