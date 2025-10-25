"""Demonstrates how to parse money amounts like `'€12.34'` or `'USD 12.34'`
into a `(currency, Decimal)` tuple using a transformation pipeline.

This example shows:
  * How to normalize various input formats (`'€12.34'`, `'usd 12.34'`, `'GBP 7.50'`).
  * How to convert the string amount into a `Decimal`.
  * How to detect invalid or unsupported currency formats gracefully.

Run directly:

    python examples/24_money_amount_decimal.py

Expected output:

    good: OK ('EUR', Decimal('12.34'))
    good2: OK ('GBP', Decimal('7.50'))
    bad : EXCEPTION Value must be one of <enum 'Currency'>, got ('AUD', Decimal('1.23'))
"""

import sys
import pathlib
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import List

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Currency(Enum):
    """Supported currencies for this example."""
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


class Strip(TransformationStrategy[str, str]):
    """Trim leading and trailing whitespace from a string."""

    def transform(self, value: str) -> Response[str]:
        """Strip whitespace from the input string.

        Args:
            value: The raw input string.

        Returns:
            Response[str]: Contains:
                * `status = Status.OK`
                * `details = "strip"`
                * `value` — the trimmed string
        """
        return Response(Status.OK, "strip", value.strip())


class NormalizeCurrencyPrefix(TransformationStrategy[str, tuple]):
    """Normalize currency prefixes and symbols.

    Accepts strings like `'EUR 12.34'`, `'€12.34'`, or `'usd 12.34'`
    and converts them into a tuple `(currency_code, amount_string)`.

    If the input cannot be parsed, the strategy returns `Status.EXCEPTION`.
    """

    SYMBOLS = {"€": "EUR", "$": "USD", "£": "GBP"}

    def transform(self, value: str) -> Response[tuple]:
        """Normalize currency and extract amount substring.

        Args:
            value: The string containing currency and amount.

        Returns:
            Response[tuple]: Contains `(currency_code, amount_str)` or
            an error response if parsing fails.
        """
        v = value.strip()
        if not v:
            return Response(Status.EXCEPTION, "empty", None)
        if v[0] in self.SYMBOLS:
            cur = self.SYMBOLS[v[0]]
            amt = v[1:].strip()
            return Response(Status.OK, "symbol", (cur, amt))
        parts = v.split(None, 1)
        if len(parts) == 2:
            cur, amt = parts[0].upper(), parts[1].strip()
            return Response(Status.OK, "prefix", (cur, amt))
        return Response(Status.EXCEPTION, "format 'CUR 12.34' or '€12.34'", None)


class ParseAmount(TransformationStrategy[tuple, tuple]):
    """Convert a `(currency, amount_string)` pair into a `(currency, Decimal)` tuple."""

    def transform(self, value: tuple) -> Response[tuple]:
        """Attempt to parse the amount as a Decimal.

        Args:
            value: Tuple `(currency_code, amount_str)`.

        Returns:
            Response[tuple]: Contains:
                * `status = Status.OK` with `(currency_code, Decimal(amount))`
                * `status = Status.EXCEPTION` if parsing fails
        """
        cur, amt_s = value
        try:
            return Response(Status.OK, "decimal", (cur, Decimal(amt_s)))
        except (InvalidOperation, ValueError) as e:
            return Response(Status.EXCEPTION, f"bad decimal: {e}", None)


from constrained_values import EnumValidationStrategy

class MoneyConfig(ConstrainedValue[tuple]):
    """A `ConstrainedValue` that parses a money amount into `(currency, Decimal)`.

    The transformation pipeline:
        1. `TypeValidationStrategy(str)` — ensures the input is a string.
        2. `Strip()` — trims leading/trailing spaces.
        3. `NormalizeCurrencyPrefix()` — extracts `(currency, amount_string)`.
        4. `ParseAmount()` — converts amount to `Decimal`.
        5. `EnumValidationStrategy(Currency)` — ensures currency is supported.
    """

    def get_strategies(self) -> List[PipeLineStrategy]:
        """Return the full transformation pipeline."""
        return [
            TypeValidationStrategy(str),
            Strip(),
            NormalizeCurrencyPrefix(),
            ParseAmount(),
            EnumValidationStrategy(Currency),
        ]



def main() -> None:
    """Run the money parsing demonstration.

    Creates several :class:`MoneyConfig` instances to parse different
    currency string formats and prints their results.

    Steps:
        1. `"€12.34"` → OK, parsed as (`'EUR'`, Decimal('12.34')).
        2. `"gbp 7.50"` → OK, parsed as (`'GBP'`, Decimal('7.50')).
        3. `"AUD 1.23"` → EXCEPTION, unsupported currency format.

    Prints:
        * `"good: OK ('EUR', Decimal('12.34'))"`
        * `"good2: OK ('GBP', Decimal('7.50'))"`
        * `"bad : EXCEPTION Value must be one of <enum 'Currency'>, got ('AUD', Decimal('1.23'))"`
    """
    good = MoneyConfig("€12.34")
    print("good:", good.status.name, good.value)
    good2 = MoneyConfig("gbp 7.50")
    print("good2:", good2.status.name, good2.value)
    bad = MoneyConfig("AUD 1.23")
    print("bad :", bad.status.name, bad.details)


if __name__ == "__main__":
    main()
