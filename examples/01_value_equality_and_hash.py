"""Demonstrates how equality and hashing work between instances of the same
`Value` subclass, and how they behave in sets and dictionaries.

This example shows:
  * Two `Value` objects with the same underlying data are equal (`==`) and
    share the same hash.
  * Distinct values are not equal and yield different hashes.
  * How Python collections (sets, dicts) handle these objects.
  * Two `Value` instances with the same wrapped data are considered equal,
  * so only one is kept in sets or dicts. In a dictionary, inserting a second
  * equal key replaces the existing entry.
  * How subclassing `Value` with different type parameters affects equality.

Run directly:

    python examples/01_value_equality_and_hash.py

Expected output:

    a == b: True
    a == c: False
    hash(a) == hash(b): True
    set size (should be 2): 2
    dict size (should be 2): 2
    dict[a] = second
    IntValue(5) == StrValue('5'): False
"""

import sys
import pathlib

# ---------------------------------------------------------------------------
# Make the repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Value


def main() -> None:
    """Run the equality and hashing demonstration.

    This function creates several instances of :class:`Value` and its subclasses
    to show how equality (`__eq__`) and hashing (`__hash__`) interact with
    Python collections.

    Examples:
        >>> a = Value(10)
        >>> b = Value(10)
        >>> a == b
        True
        >>> hash(a) == hash(b)
        True

    Prints:
        Results of equality and hashing comparisons, and the sizes of a set
        and dict containing Value instances.
    """
    a = Value(10)
    b = Value(10)
    c = Value(20)

    print("a == b:", a == b)
    print("a == c:", a == c)
    print("hash(a) == hash(b):", hash(a) == hash(b))

    s = {a, b, c}
    print("set size (should be 2):", len(s))

    d = {a: "first", b: "second", c: "third"}
    print("dict size (should be 2):", len(d))
    print("dict[a] =", d[a])

    class IntValue(Value[int]):
        """A Value subclass specialized for integers.

        Demonstrates how subclassing `Value` allows type-specific variants that
        still participate in equality and hashing based on contained data.
        """
        pass

    class StrValue(Value[str]):
        """A Value subclass specialized for strings."""
        pass

    print("IntValue(5) == StrValue('5'):", IntValue(5) == StrValue("5"))


if __name__ == "__main__":
    main()
