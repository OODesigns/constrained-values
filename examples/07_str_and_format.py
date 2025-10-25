"""Demonstrates how valid and invalid `ConstrainedValue` objects behave when
formatted with `str()` or `format()`.

This example shows:
  * A successful value supports numeric formatting (e.g., `.2f`).
  * A failed value falls back to `str()` representation when formatting fails.
  * The `details` field differentiates success vs. failure.

Run directly:

    python examples/07_str_and_format.py

Expected output:

    format ok .2f: 12.35
    format bad .2f (falls back to str): <invalid BadF: boom fmt>
    str(bad): <invalid BadF: boom fmt>
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
    """A transformation strategy that always succeeds.

    Produces an `OK` response with the input value unchanged.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return an OK response with the input value.

        Args:
            value: Any input value to pass through.

        Returns:
            Response[Any]: Contains `status=Status.OK`,
            `details='ok fmt'`, and the same `value`.
        """
        return Response(status=Status.OK, details="ok fmt", value=value)


class Fail(TransformationStrategy[Any, Any]):
    """A transformation strategy that always fails.

    Used to demonstrate how formatting behaves for invalid constrained values.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return a failed response.

        Args:
            value: Any input value (ignored).

        Returns:
            Response[Any]: Contains `status=Status.EXCEPTION`,
            `details='boom fmt'`, and `value=None`.
        """
        return Response(status=Status.EXCEPTION, details="boom fmt", value=None)


class GoodF(ConstrainedValue[float]):
    """A `ConstrainedValue[float]` that always succeeds."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step success pipeline."""
        return [Pass()]


class BadF(ConstrainedValue[float]):
    """A `ConstrainedValue[float]` that always fails."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step failure pipeline."""
        return [Fail()]


def main() -> None:
    """Run the `__str__` and `__format__` demonstration.

    Creates two constrained values:
      * `GoodF` → succeeds and supports numeric formatting (e.g., `".2f"`).
      * `BadF` → fails and falls back to its `str()` representation.

    Prints:
        * Formatted output for the successful value (`12.35`)
        * Formatted output for the failed value (string fallback)
        * Direct `str()` representation of the failed value
    """
    ok = GoodF(12.3456)
    bad = BadF(12.3456)

    print("format ok .2f:", format(ok, ".2f"))
    print("format bad .2f (falls back to str):", format(bad, ".2f"))
    print("str(bad):", str(bad))


if __name__ == "__main__":
    main()
