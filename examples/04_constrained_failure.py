"""
Example 04 — Failing ConstrainedValue
A ConstrainedValue that fails in its pipeline and exposes status/details.
"""
from typing import Any, List

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Fail(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.EXCEPTION, details="boom", value=None)

class Broken(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [Fail()]

def main():
    y = Broken(999)
    print("status:", y.status.name)
    print("details:", y.details)
    print("value:", y.value)

if __name__ == "__main__":
    main()
