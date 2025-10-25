"""Demonstrates how sorting a list containing both valid and invalid
:class:`ConstrainedValue` instances results in an error.

This example shows:
  * Valid constrained values (`Status.OK`) are comparable and sortable.
  * Invalid values (`Status.EXCEPTION`) cannot be meaningfully compared.
  * Sorting such a mixed list raises a `TypeError`.

Run directly:

    python examples/20_sorting_with_invalid.py

Expected output:

    sort raised: '<' not supported between instances of 'Bad' and 'Good'
"""

import sys
import pathlib
from typing import Any, List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Pass(TransformationStrategy[Any, Any]):
    """A transformation that always succeeds."""

    def transform(self, value: Any) -> Response[Any]:
        """Return a successful response with the input value unchanged.

        Args:
            value: The input to pass through.

        Returns:
            Response[Any]: Contains:
                * `status = Status.OK`
                * `details = "ok"`
                * `value` equal to the input
        """
        return Response(status=Status.OK, details="ok", value=value)


class Fail(TransformationStrategy[Any, Any]):
    """A transformation that always fails."""

    def transform(self, value: Any) -> Response[Any]:
        """Return a failed response with no usable value.

        Args:
            value: Any input value (ignored).

        Returns:
            Response[Any]: Contains:
                * `status = Status.EXCEPTION`
                * `details = "bad"`
                * `value = None`
        """
        return Response(status=Status.EXCEPTION, details="bad", value=None)


class Good(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that always succeeds."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step successful pipeline."""
        return [Pass()]


class Bad(ConstrainedValue[int]):
    """A `ConstrainedValue[int]` that always fails."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return a one-step failing pipeline."""
        return [Fail()]


def main() -> None:
    """Run the sorting demonstration.

    Creates a mixed list of valid and invalid constrained values and attempts
    to sort it. Because invalid values cannot be compared meaningfully, a
    `TypeError` is raised.

    Steps:
        1. Create `[Good(3), Bad(99), Good(1)]`.
        2. Attempt to `list.sort()`.
        3. Catch and print the resulting `TypeError`.

    Prints:
        * `"sort raised: '<' not supported between instances of 'Bad' and 'Good'"`
    """
    items = [Good(3), Bad(99), Good(1)]
    try:
        items.sort()
    except TypeError as e:
        print("sort raised:", e)


if __name__ == "__main__":
    main()
