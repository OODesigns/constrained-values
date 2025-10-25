"""Demonstrates parsing date strings in multiple formats and validating that the
resulting date is within an acceptable range.

This example shows:
  * How to accept multiple common date formats (ISO, European, etc.).
  * How to convert strings into `datetime.date` objects via a transformation pipeline.
  * How to use :class:`RangeValue` to validate that a parsed date lies within
    a specified valid range.

Supported formats:
  * `"%Y-%m-%d"` → ISO format (e.g., `"2000-01-31"`)
  * `"%d/%m/%Y"` → European format (e.g., `"31/01/2000"`)
  * `"%d-%b-%Y"` → Month abbreviation (e.g., `"31-Jan-2000"`)

Run directly:

    python examples/28_date_parsing.py

Expected output:

    parsed: OK 2000-01-31
    in-range: OK
"""

import sys
import pathlib
from datetime import date, datetime
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, TypeValidationStrategy, RangeValue
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]


class ToDate(TransformationStrategy[str, date]):
    """Transform a string into a `datetime.date` object using multiple formats."""

    def transform(self, value: str) -> Response[date]:
        """Attempt to parse a date from the input string using known formats.

        Args:
            value: The input date string.

        Returns:
            Response[date]:
                * `status = Status.OK` and the parsed date if successful.
                * `status = Status.EXCEPTION` and an error message if all formats fail.
        """
        v = value.strip()
        for fmt in FORMATS:
            try:
                parsed = datetime.strptime(v, fmt).date()
            except ValueError:
                continue  # Try the next format
            else:
                return Response(Status.OK, fmt, parsed)
        return Response(Status.EXCEPTION, f"no matching formats for {v!r}; tried {FORMATS}", None)


class BirthDate(ConstrainedValue[date]):
    """A constrained value that parses and validates date strings."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the transformation pipeline (string → date)."""
        return [TypeValidationStrategy(str), ToDate()]


def main() -> None:
    """Run the date parsing and range validation demonstration.

    Steps:
        1. Parse a valid date string using `BirthDate`.
        2. Validate the parsed date against a valid range using `RangeValue`.

    Prints:
        * `"parsed: OK 2000-01-31"`
        * `"in-range: OK"`
    """
    d = BirthDate("2000-01-31")
    print("parsed:", d.status.name, d.value)
    r = RangeValue(d.value, date(1900, 1, 1), date(2100, 1, 1))
    print("in-range:", r.status.name)


if __name__ == "__main__":
    main()
