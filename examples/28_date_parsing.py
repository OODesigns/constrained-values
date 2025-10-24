"""
Example 28 — Date parsing and range
Parse multiple formats into date and validate in range.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from datetime import date, datetime
from typing import List
from constrained_values import Response, Status, TypeValidationStrategy, RangeValue
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

FORMATS = ["%Y-%m-%d", "%d/%m/%Y", "%d-%b-%Y"]

class ToDate(TransformationStrategy[str, date]):
    def transform(self, value: str) -> Response[date]:
        v = value.strip()
        for fmt in FORMATS:
            try:
                parsed = datetime.strptime(v, fmt).date()
            except ValueError:
                continue  # try the next format
            else:
                return Response(Status.OK, fmt, parsed)
        return Response(Status.EXCEPTION, f"no matching formats for {v!r}; tried {FORMATS}", None)


class BirthDate(ConstrainedValue[date]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [TypeValidationStrategy(str), ToDate()]

def main():
    d = BirthDate("2000-01-31")
    print("parsed:", d.status.name, d.value)
    r = RangeValue(d.value, date(1900, 1, 1), date(2100, 1, 1))
    print("in-range:", r.status.name)

if __name__ == "__main__":
    main()
