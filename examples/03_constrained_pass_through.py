"""
Example 03 — Minimal ConstrainedValue
A ConstrainedValue that simply passes the value through.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import Any, List

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class PassThrough(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.OK, details="ok", value=value)

class MyNumber(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [PassThrough()]

def main():
    x = MyNumber(123)
    print("status:", x.status.name)
    print("value:", x.value)

if __name__ == "__main__":
    main()
