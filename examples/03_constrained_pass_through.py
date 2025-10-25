"""Demonstrates the smallest useful `ConstrainedValue` implementation: a single
transformation strategy that **accepts any input** and returns it unchanged.

What this shows:
  * How to define a `TransformationStrategy` that always returns `Status.OK`.
  * How to plug that strategy into a `ConstrainedValue` via `get_strategies()`.
  * How to read the resulting `status` and `value`.

Run directly:

    python examples/03_constrained_pass_through.py

Expected output:

    status: OK
    value: 123
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


class PassThrough(TransformationStrategy[Any, Any]):
    """A transformation strategy that accepts the input as-is.

    This strategy always returns `Status.OK` and echoes the input `value`
    unchanged. It’s useful as a baseline or for wiring tests where no
    validation or transformation is needed.
    """

    def transform(self, value: Any) -> Response[Any]:
        """Return the input value unchanged with an OK status.

        Args:
            value: The input to pass through.

        Returns:
            Response[Any]: A response carrying:
                * `status = Status.OK`
                * `details = "ok"`
                * `value` equal to the input
        """
        return Response(status=Status.OK, details="ok", value=value)


class MyNumber(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that uses the pass-through strategy.

    The pipeline contains a single `PassThrough` step, so any integer is
    accepted and propagated unchanged.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the pipeline of strategies for this constrained value.

        Returns:
            List[PipeLineStrategy]: A single-step pipeline with `PassThrough`.
        """
        return [PassThrough()]


def main() -> None:
    """Run the pass-through demonstration.

    Creates a :class:`MyNumber` with the input `123` and prints the resulting
    `status` and `value`.

    Prints:
        The status name (expected: `OK`) and the value (expected: `123`).
    """
    x = MyNumber(123)
    print("status:", x.status.name)
    print("value:", x.value)


if __name__ == "__main__":
    main()
