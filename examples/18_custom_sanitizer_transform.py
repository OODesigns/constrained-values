"""Demonstrates a multi-step sanitization and validation pipeline that trims
and lowercases user input before applying type and enumeration validation.

This example shows:
  * How to compose multiple string preprocessing transformations.
  * How to validate cleaned strings against an allowed list of values.
  * How a value passes through sequential strategies before validation.

Run directly:

    python examples/18_custom_sanitizer_transform.py

Expected output:

    x: OK apple
    y: EXCEPTION Value must be one of ('apple', 'pear', 'plum'), got banana
"""

import sys
import pathlib
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, TypeValidationStrategy, EnumValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Trim(TransformationStrategy[str, str]):
    """A transformation that removes leading and trailing whitespace."""

    def transform(self, value: str) -> Response[str]:
        """Trim the input string.

        Args:
            value: The input string.

        Returns:
            Response[str]: Contains:
                * `status = Status.OK`
                * `details = "trim"`
                * `value` — the trimmed string
        """
        return Response(status=Status.OK, details="trim", value=value.strip())


class Lower(TransformationStrategy[str, str]):
    """A transformation that converts input text to lowercase."""

    def transform(self, value: str) -> Response[str]:
        """Convert the string to lowercase.

        Args:
            value: The input string.

        Returns:
            Response[str]: Contains:
                * `status = Status.OK`
                * `details = "lower"`
                * `value` — the lowercase string
        """
        return Response(status=Status.OK, details="lower", value=value.lower())


class CleanFruit(ConstrainedValue[str]):
    """A constrained string value that sanitizes and validates fruit names.

    The transformation pipeline performs the following steps:
        1. `Trim()` — remove leading/trailing spaces.
        2. `Lower()` — convert to lowercase.
        3. `TypeValidationStrategy(str)` — ensure the value is a string.
        4. `EnumValidationStrategy(("apple", "pear", "plum"))` — check membership.

    Inputs that pass all transformations and validations yield `Status.OK`.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the sanitization and validation pipeline."""
        return [
            Trim(),
            Lower(),
            TypeValidationStrategy(str),
            EnumValidationStrategy(("apple", "pear", "plum")),
        ]


def main() -> None:
    """Run the custom sanitizer demonstration.

    Creates two :class:`CleanFruit` constrained values:
        1. Input `"  Apple  "` — trimmed, lowercased, and validated → OK.
        2. Input `" Banana "` — not in the allowed list → EXCEPTION.

    Prints:
        * `"x: OK apple"`
        * `"y: EXCEPTION Value must be one of ('apple', 'pear', 'plum'), got banana"`
    """
    x = CleanFruit("  Apple  ")
    y = CleanFruit(" Banana ")
    print("x:", x.status.name, x.value)
    print("y:", y.status.name, y.details)


if __name__ == "__main__":
    main()
