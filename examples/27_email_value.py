"""Demonstrates trimming, lowercasing, and validating a simple email address
using a :class:`ConstrainedValue` pipeline.

This example shows:
  * How to normalize email addresses by trimming and lowercasing.
  * How to validate them against a simple regex pattern.
  * How to override `__bool__` to indicate email validity directly.

> ⚠️ Note: This regex is intentionally minimal and not fully RFC 5322–compliant.
  It is only for basic demonstration of pipeline validation.

Run directly:

    python examples/27_email_value.py

Expected output:

    e1: True alice@example.com
    e2: False bad@@example
"""

import sys
import pathlib
import re
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

# Simple demonstration regex (non-exhaustive, but good for basic structure)
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class TrimLower(TransformationStrategy[str, str]):
    """Normalize an email string by trimming spaces and converting to lowercase."""

    def transform(self, value: str) -> Response[str]:
        """Trim whitespace and lowercase the input string.

        Args:
            value: The input email string.

        Returns:
            Response[str]: Contains:
                * `status = Status.OK`
                * `details = "normalize"`
                * `value` — the normalized string
        """
        return Response(Status.OK, "normalize", value.strip().lower())


class Email(ConstrainedValue[str]):
    """A constrained value representing a normalized email address."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the email normalization pipeline."""
        return [TypeValidationStrategy(str), TrimLower()]

    def __bool__(self) -> bool:
        """Return `True` if the email passes normalization and regex validation."""
        return self.ok and bool(EMAIL_RE.match(self.value))


def main() -> None:
    """Run the email normalization and validation demonstration.

    Steps:
        1. Create an `Email` with extra spaces and uppercase letters.
        2. Create an invalid email with multiple `@` symbols.
        3. Print the boolean validity and normalized value for each.

    Prints:
        * `"e1: True alice@example.com"`
        * `"e2: False bad@@example"`
    """
    e1 = Email("  Alice@Example.com ")
    print("e1:", bool(e1), e1.value)
    e2 = Email("bad@@example")
    print("e2:", bool(e2), e2.value)


if __name__ == "__main__":
    main()
