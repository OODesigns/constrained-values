"""Demonstrates how ordering between `Value` objects works **within** the same
concrete subclass, and that the reflected comparison (`__lt__`) of the other
object is *not* used when the left-hand operand implements ordering itself.

This ensures that ordering semantics are consistent and predictable: comparisons
like `x > y` and `x < y` only rely on the appropriate methods from the same
class, rather than accidentally invoking reflected operations.

Run directly:

    python examples/02_value_ordering_same_class.py

Expected output:

    x > y: True
"""

import sys
import pathlib

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Value


class BreakLtSame(Value[int]):
    """A subclass of `Value[int]` that intentionally breaks `__lt__`.

    This class is used to verify that when performing a comparison like
    ``x > y``, the `Value` base class uses its own `__gt__` implementation
    rather than falling back to the reflected ``__lt__`` on the other operand.

    Attempting to use ``<`` with this class will raise a `RuntimeError` so
    it’s obvious if the wrong comparison path is taken.
    """

    def __init__(self, v: int) -> None:
        """Initialize a `BreakLtSame` instance.

        Args:
            v: The integer value to wrap.
        """
        super().__init__(v)

    def __lt__(self, other) -> bool:  # pragma: no cover (sentinel)
        """Deliberately raise an error if `__lt__` is called.

        This sentinel ensures that the test only passes if the `Value`
        base class handles `>` (greater than) comparisons internally,
        without triggering this reflected method.
        """
        raise RuntimeError("Reflected __lt__ should not be used")


def main() -> None:
    """Run the ordering comparison demonstration.

    Creates two instances of :class:`BreakLtSame` with different underlying
    integer values, then compares them using ``>``.

    The comparison should **not** call the subclass’s broken `__lt__`;
    instead, it should use `Value.__gt__`, resulting in a successful and
    correct comparison.

    Prints:
        The boolean result of `x > y`, which should be `True`.
    """
    x = BreakLtSame(2)
    y = BreakLtSame(1)
    print("x > y:", x > y)  # uses __gt__ on Value; won't call reflected __lt__


if __name__ == "__main__":
    main()
