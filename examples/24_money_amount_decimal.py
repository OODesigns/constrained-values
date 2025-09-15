"""
Example 24 — Money amount parsing
Parse '€12.34' or 'USD 12.34' into (currency, Decimal) using transforms.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from decimal import Decimal, InvalidOperation
from enum import Enum
from typing import List
from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class Currency(Enum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"

class Strip(TransformationStrategy[str, str]):
    def transform(self, value: str) -> Response[str]:
        return Response(Status.OK, "strip", value.strip())

class NormalizeCurrencyPrefix(TransformationStrategy[str, tuple]):
    """Accept 'EUR 12.34', '€12.34', 'usd 12.34' → ('EUR', '12.34')"""
    SYMBOLS = {"€": "EUR", "$": "USD", "£": "GBP"}
    def transform(self, value: str) -> Response[tuple]:
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
    def transform(self, value: tuple) -> Response[tuple]:
        cur, amt_s = value
        try:
            return Response(Status.OK, "decimal", (cur, Decimal(amt_s)))
        except (InvalidOperation, ValueError) as e:
            return Response(Status.EXCEPTION, f"bad decimal: {e}", None)

class MoneyConfig(ConstrainedValue[tuple]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [TypeValidationStrategy(str), Strip(), NormalizeCurrencyPrefix(), ParseAmount()]

def main():
    good = MoneyConfig("€12.34")
    print("good:", good.status.name, good.value)
    good2 = MoneyConfig("gbp 7.50")
    print("good2:", good2.status.name, good2.value)
    bad = MoneyConfig("AUD 1.23")
    print("bad :", bad.status.name, bad.details)

if __name__ == "__main__":
    main()
