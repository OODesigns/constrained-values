"""Demonstrates how the `.unwrap()` method of a `ConstrainedValue` behaves.

This example shows:
  * When the status is `Status.OK`, `.unwrap()` returns the underlying
    canonical value.
  * When the status is not OK (e.g. `Status.EXCEPTION`), `.unwrap()` raises
    a `ValueError` containing the failure details.

Run directly:

    python examples/06_unwrap_usage.py

Expected output:

    unwrap OK: 456
    caught: Bad invalid: boom unwrap
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
    PipeLineStrategy,
    ConstrainedValue,
)


class Pass(TransformationStrategy[Any, Any]):
    """A transformation strategy that always succeeds.

    This simply passes the input value through unchanged, returning an
    OK `Response`.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return the input value with an OK status.

        Args:
            value: The input to pass through.

        Returns:
            Response[Any]: A successful response containing:
                * `status = Status.OK`
                * `details = "ok"`
                * `value` equal to the input
        """
        return Response(status=Status.OK, details="ok", value=value)


class Fail(TransformationStrategy[Any, Any]):
    """A transformation strategy that always fails.

    Used to show how `.unwrap()` raises when the `ConstrainedValue` has
    a non-OK status.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return a failure response.

        Args:
            value: Any input value (ignored).

        Returns:
            Response[Any]: A failed response with:
                * `status = Status.EXCEPTION`
                * `details = "boom unwrap"`
                * `value = None`
        """
        return Response(status=Status.EXCEPTION, details="boom unwrap", value=None)


class Good(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that always succeeds."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step pass-through pipeline."""
        return [Pass()]


class Bad(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that always fails."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step failing pipeline."""
        return [Fail()]


def main() -> None:
    """Run the `.unwrap()` demonstration.

    Creates one successful and one failing constrained value, and shows
    how `.unwrap()` behaves for each.

    Steps:
        1. `Good(456)` unwraps successfully and prints the value.
        2. `Bad(999)` raises a `ValueError`, which is caught and printed.

    Prints:
        * `"unwrap OK: 456"`
        * `"caught: Bad invalid: boom unwrap"`
    """
    x = Good(456)
    print("unwrap OK:", x.unwrap())

    y = Bad(999)
    try:
        print("unwrap BAD (should raise):", y.unwrap())
    except ValueError as e:
        print("caught:", e)


if __name__ == "__main__":
    main()
