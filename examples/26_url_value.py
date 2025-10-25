"""Demonstrates how to parse and validate URLs using a transformation pipeline
built on :class:`ConstrainedValue`.

This example shows:
  * How to convert a string into a parsed `urllib.parse.ParseResult`.
  * How to validate that the URL includes both a scheme and host.
  * How failures produce `Status.EXCEPTION` with a descriptive error message.

Run directly:

    python examples/26_url_value.py

Expected output:

    ok : OK https://example.com/path?q=1
    bad: EXCEPTION missing scheme or host
"""

import sys
import pathlib
from typing import List
from urllib.parse import urlparse, ParseResult

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class ToURL(TransformationStrategy[str, ParseResult]):
    """Transform a string into a parsed URL using `urllib.parse.urlparse`."""

    def transform(self, value: str) -> Response[ParseResult]:
        """Parse and validate the URL string.

        Args:
            value: The input string representing a URL.

        Returns:
            Response[ParseResult]:
                * `Status.OK` and parsed `ParseResult` if the URL includes
                  a valid scheme and host.
                * `Status.EXCEPTION` and a message if missing scheme or host.
        """
        p = urlparse(value)
        if not p.scheme or not p.netloc:
            return Response(Status.EXCEPTION, "missing scheme or host", None)
        return Response(Status.OK, "parsed", p)


class HttpURL(ConstrainedValue[ParseResult]):
    """A constrained value that parses and validates URLs."""

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the URL parsing and validation pipeline."""
        return [TypeValidationStrategy(str), ToURL()]


def main() -> None:
    """Run the URL validation demonstration.

    Creates two :class:`HttpURL` instances — one valid and one invalid — and
    prints their resulting status and details.

    Steps:
        1. Valid URL → OK, printed as full URL string.
        2. Invalid URL → EXCEPTION, printed with error details.

    Prints:
        * `"ok : OK https://example.com/path?q=1"`
        * `"bad: EXCEPTION missing scheme or host"`
    """
    ok = HttpURL("https://example.com/path?q=1")
    bad = HttpURL("not-a-url")

    if ok.ok:
        parsed = ok.value
        print("ok :", ok.status.name, parsed.geturl())
    else:
        print("ok :", ok.status.name, ok.details)

    print("bad:", bad.status.name, bad.details)


if __name__ == "__main__":
    main()
