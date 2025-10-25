"""Demonstrates how the truthiness (`bool()`) and `.ok` attribute of a
`ConstrainedValue` instance mirror its internal `Status.OK` state.

This example shows:
  * A successful value returns `True` for both `.ok` and `bool(instance)`.
  * A failed value returns `False` for both.
  * How to access `details` for additional diagnostic information.

Run directly:

    python examples/05_truthiness_and_ok.py

Expected output:

    g.ok, bool(g) g.details: True True ok
    b.ok, bool(b) b.details: False False nope, nothing to see here
"""

import sys
import pathlib
from typing import Any, List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status
from constrained_values.value import (
    TransformationStrategy,
    ConstrainedValue,
    PipeLineStrategy,
)


class Pass(TransformationStrategy[Any, Any]):
    """A strategy that always succeeds.

    This transformation simply returns the input value unchanged with
    `Status.OK`, simulating a successful validation or transformation step.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return an OK response with the value unchanged.

        Args:
            value: The input to pass through.

        Returns:
            Response[Any]: Contains `status=Status.OK`, `details='ok'`, and
            the same `value`.
        """
        return Response(status=Status.OK, details="ok", value=value)


class Fail(TransformationStrategy[Any, Any]):
    """A strategy that always fails.

    This demonstrates how a `ConstrainedValue` propagates a non-OK status and
    becomes falsy when evaluated in a boolean context.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return a failed response.

        Args:
            value: Any input value (ignored).

        Returns:
            Response[Any]: Contains `status=Status.EXCEPTION`,
            `details='nope, nothing to see here'`, and `value=None`.
        """
        return Response(
            status=Status.EXCEPTION,
            details="nope, nothing to see here",
            value=None,
        )


class Good(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that always succeeds.

    The pipeline consists of a single `Pass` strategy.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step pass-through pipeline."""
        return [Pass()]


class Bad(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that always fails.

    The pipeline consists of a single `Fail` strategy.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step failing pipeline."""
        return [Fail()]


def main() -> None:
    """Run the truthiness and `.ok` demonstration.

    Creates one successful (:class:`Good`) and one failing (:class:`Bad`)
    constrained value, then prints their `.ok` property, `bool()` result,
    and `.details`.

    Prints:
        - `g.ok, bool(g), g.details` → `True True validation successful`
        - `b.ok, bool(b), b.details` → `False False nope, nothing to see here`
    """
    g, b = Good(1), Bad(2)
    print("g.ok, bool(g) g.details:", g.ok, bool(g), g.details)
    print("b.ok, bool(b) b.details:", b.ok, bool(b), b.details)


if __name__ == "__main__":
    main()
