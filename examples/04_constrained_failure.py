"""Demonstrates how a `ConstrainedValue` behaves when one of its transformation
strategies fails. This example shows:

  * How a `TransformationStrategy` can signal failure with `Status.EXCEPTION`.
  * How a `ConstrainedValue` exposes its failure status, details, and value.
  * What a failed value looks like in use.

Run directly:

    python examples/04_constrained_failure.py

Expected output:

    status: EXCEPTION
    details: boom
    value: None
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


class Fail(TransformationStrategy[Any, Any]):
    """A transformation strategy that always fails.

    This intentionally raises a failure condition to demonstrate how a
    `ConstrainedValue` reacts when a pipeline step produces an error.

    Methods:
        transform: Always returns a `Response` with `Status.EXCEPTION`.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Simulate a failure transformation.

        Args:
            value: Any input value (ignored).

        Returns:
            Response[Any]: A response object containing:
                * `status = Status.EXCEPTION`
                * `details = "boom"`
                * `value = None`
        """
        return Response(status=Status.EXCEPTION, details="boom", value=None)


class Broken(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` whose pipeline always fails.

    The single pipeline step is a `Fail` strategy, so any input value will
    result in `Status.EXCEPTION` and a `None` output value.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the failing strategy pipeline.

        Returns:
            List[PipeLineStrategy]: A single-element list containing `Fail()`.
        """
        return [Fail()]


def main() -> None:
    """Run the failure demonstration.

    Creates a :class:`Broken` constrained value with input `999` and prints its
    resulting `status`, `details`, and `value`.

    Prints:
        * The status name (`EXCEPTION`)
        * The details string (`boom`)
        * The resulting value (`None`)
    """
    y = Broken(999)
    print("status:", y.status.name)
    print("details:", y.details)
    print("value:", y.value)


if __name__ == "__main__":
    main()
