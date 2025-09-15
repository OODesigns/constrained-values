"""
Example 07 — __str__ and __format__
Formatting valid vs invalid constrained values.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import Any, List

from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class Pass(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.OK, details="ok fmt", value=value)

class Fail(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]:
        return Response(status=Status.EXCEPTION, details="boom fmt", value=None)

class GoodF(ConstrainedValue[float]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Pass()]

class BadF(ConstrainedValue[float]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Fail()]

def main():
    ok = GoodF(12.3456)
    bad = BadF(12.3456)
    print("format ok .2f:", format(ok, ".2f"))
    print("format bad .2f (falls back to str):", format(bad, ".2f"))
    print("str(bad):", str(bad))

if __name__ == "__main__":
    main()
