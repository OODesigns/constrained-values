"""
Example 05 — Truthiness and .ok
bool(instance) and .ok mirror Status.OK.
"""
from typing import Any, List

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Pass(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.OK, details="ok", value=value)

class Fail(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.EXCEPTION, details="nope, nothing to see here", value=None)

class Good(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Pass()]

class Bad(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Fail()]

def main():
    g, b = Good(1), Bad(2)
    print("g.ok, bool(g) g.details:", g.ok, bool(g), g.details)
    print("b.ok, bool(b) b.details:", b.ok, bool(b), b.details)

if __name__ == "__main__":
    main()
