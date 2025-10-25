"""Demonstrates transforming a string into a `uuid.UUID` and inspecting the
resulting UUID object (including its version).

This example shows:
  * How to accept a string input and parse it into `uuid.UUID`.
  * How failures produce `Status.EXCEPTION` with an explanatory message.
  * How to access fields on the resulting UUID (e.g., `.version`) when OK.

Run directly:

    python examples/25_uuid_value.py

Expected output (example):

    x: OK 12345678-1234-5678-1234-567812345678
    y: OK 4
"""

import sys
import pathlib
import uuid
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import (
    TransformationStrategy,
    ConstrainedValue,
    PipeLineStrategy,
)


class ToUUID(TransformationStrategy[str, uuid.UUID]):
    """Transform a string into a `uuid.UUID`."""

    def transform(self, value: str) -> Response[uuid.UUID]:
        """Attempt to parse a UUID from the input string.

        Args:
            value: The input string to parse as a UUID.

        Returns:
            Response[uuid.UUID]:
                * `status = Status.OK`, `details = "uuid"`, and a `uuid.UUID`
                  instance when parsing succeeds.
                * `status = Status.EXCEPTION` and an error message when parsing
                  fails.
        """
        try:
            return Response(Status.OK, "uuid", uuid.UUID(value))
        except Exception as e:
            return Response(Status.EXCEPTION, f"bad uuid: {e}", None)


class UUIDValue(ConstrainedValue[uuid.UUID]):
    """A `ConstrainedValue` that parses strings into `uuid.UUID`."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the parsing pipeline (string → UUID)."""
        return [TypeValidationStrategy(str), ToUUID()]


def main() -> None:
    """Run the UUID parsing demonstration.

    Steps:
        1. Parse a fixed UUID string and print either the parsed value (OK)
           or the error details (EXCEPTION).
        2. Parse a newly generated v4 UUID string and print its `.version`.

    Prints:
        * `"x: OK <uuid-string>"` or `"x: EXCEPTION <details>"`
        * `"y: OK 4"` (for a freshly generated v4 UUID)
    """
    x = UUIDValue("12345678-1234-5678-1234-567812345678")
    print("x:", x.status.name, x.value if x.ok else x.details)

    y = UUIDValue(str(uuid.uuid4()))
    print("y:", y.status.name, y.value.version if y.ok else y.details)


if __name__ == "__main__":
    main()
