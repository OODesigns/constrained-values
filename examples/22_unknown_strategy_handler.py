"""Demonstrates how the framework handles a pipeline strategy that does not
implement either the transformation or validation interface.

This example shows:
  * A subclass of :class:`PipeLineStrategy` that provides no transformation
    or validation behavior.
  * The resulting :class:`ConstrainedValue` fails with `Status.EXCEPTION`.
  * The failure details explain that the strategy type is unsupported.

Run directly:

    python examples/22_unknown_strategy_handler.py

Expected output:

    status: EXCEPTION
    details: Missing strategy handler
"""

import sys
import pathlib

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values.value import PipeLineStrategy, ConstrainedValue


class Unknown(PipeLineStrategy):
    """A pipeline strategy that implements neither transform nor validation.

    Used to test how :class:`ConstrainedValue` responds when it encounters an
    unrecognized strategy type. This should trigger an internal exception
    path, resulting in `Status.EXCEPTION`.
    """
    pass


class UsesUnknown(ConstrainedValue[int]):
    """A `ConstrainedValue` subclass that includes an invalid strategy."""

    def get_strategies(self):
        """Return a pipeline containing one unknown, invalid strategy."""
        return [Unknown()]


def main() -> None:
    """Run the unknown-strategy demonstration.

    Creates an instance of :class:`UsesUnknown` containing an unsupported
    pipeline strategy. The value initialization fails internally and sets:

      * `status = Status.EXCEPTION`
      * `details` to a description of the invalid strategy type.

    Prints:
        * `"status: EXCEPTION"`
        * `"details: Missing strategy handler"`
    """
    x = UsesUnknown(5)
    print("status:", x.status.name)
    print("details:", x.details)


if __name__ == "__main__":
    main()
