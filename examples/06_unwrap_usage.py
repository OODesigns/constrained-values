"""
Example 06 — unwrap()
Return canonical value when OK; raises on invalid.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import Any, List
from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, PipeLineStrategy, ConstrainedValue

class Pass(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.OK, details="ok", value=value)

class Fail(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.EXCEPTION, details="boom unwrap", value=None)

class Good(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Pass()]

class Bad(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Fail()]

def main():
    x = Good(456)
    print("unwrap OK:", x.unwrap())
    y = Bad(999)
    try:
        print("unwrap BAD (should raise):", y.unwrap())
    except ValueError as e:
        print("caught:", e)

if __name__ == "__main__":
    main()
