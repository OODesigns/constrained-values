"""Demonstrates how to record detailed step-by-step logs for every
transformation in a :class:`ConstrainedValue` pipeline.

This example shows:
  * How each transformation step records both input and output values.
  * How to store these logs in a per-strategy list.
  * How exceptions are caught and logged without aborting the pipeline.

Run directly:

    python examples/30_pipeline_logging.py

Expected output:

    ('strip', 'OK', '  hi  ', 'hi')
    ('upper', 'OK', 'hi', 'HI')
    ('suffix', 'OK', 'HI', 'HI_X')
    final: OK HI_X
"""

import sys
import pathlib
from typing import Any, List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue


class LogStep(TransformationStrategy[Any, Any]):
    """A transformation strategy that logs every step of the pipeline.

    Attributes:
        tag (str): Label identifying this step (e.g., "strip" or "upper").
        fn (Callable[[Any], Any]): Transformation function applied to the value.
        logs (List[Tuple[str, str, Any, Any]]): Recorded results per invocation.
    """

    def __init__(self, tag: str, fn):
        """Initialize the logging strategy.

        Args:
            tag: Human-readable identifier for the step.
            fn: Callable performing the transformation, e.g. `lambda s: s.upper()`.
        """
        self.tag = tag
        self.fn = fn
        self.logs: List[tuple] = []

    def transform(self, value: Any) -> Response[Any]:
        """Apply the transformation and record the outcome.

        Args:
            value: The input value passed down the pipeline.

        Returns:
            Response[Any]: Successful or failed transformation result.
        """
        try:
            new_value = self.fn(value)
            self.logs.append((self.tag, "OK", value, new_value))
            return Response(Status.OK, self.tag, new_value)
        except Exception as e:
            self.logs.append((self.tag, "EX", value, str(e)))
            return Response(Status.EXCEPTION, f"{self.tag}: {e}", None)


class LoggedValue(ConstrainedValue[Any]):
    """A `ConstrainedValue` subclass that uses logging strategies.

    The pipeline for this example:
        1. `strip` — remove leading/trailing spaces.
        2. `upper` — convert to uppercase.
        3. `suffix` — append `"_X"`.
    """

    __slots__ = ("_strategies",)

    def __init__(self, value: Any):
        """Initialize the pipeline with predefined logging steps."""
        steps: List[LogStep] = [
            LogStep("strip", lambda s: s.strip()),
            LogStep("upper", lambda s: s.upper()),
            LogStep("suffix", lambda s: s + "_X"),
        ]
        object.__setattr__(self, "_strategies", steps)
        super().__init__(value)

    def get_strategies(self) -> List[LogStep]:
        """Return the pipeline of logging strategies."""
        return self._strategies


def main() -> None:
    """Run the pipeline logging demonstration.

    Creates a `LoggedValue` from `"  hi  "` and prints all recorded logs.

    Each pipeline step stores a tuple of:
        `(step_name, status, input_value, output_value)`

    Prints:
        * Each logged tuple from every strategy.
        * `"final: OK HI_X"` — the overall result.
    """
    x = LoggedValue("  hi  ")
    for s in x.get_strategies():
        for entry in s.logs:
            print(entry)
    print("final:", x.status.name, x.value)


if __name__ == "__main__":
    main()
