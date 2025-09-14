"""
Example 20 — Sorting with invalid present
Attempting to sort a list containing an invalid ConstrainedValue raises ValueError.
"""
from typing import Any, List

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Pass(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]: return Response(status=Status.OK, details="ok", value=value)

class Fail(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]: return Response(status=Status.EXCEPTION, details="bad", value=None)

class Good(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Pass()]

class Bad(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Fail()]

def main():
    items = [Good(3), Bad(99), Good(1)]
    try:
        items.sort()
    except TypeError as e:
        print("sort raised:", e)

if __name__ == "__main__":
    main()
