"""
Example 09 — Chained transforms
Running multiple transformation steps before final validation.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import List
from constrained_values import Response, Status, RangeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class Inc(TransformationStrategy[int, int]):
    def transform(self, value: int) -> Response[int]:
        return Response(status=Status.OK, details="inc", value=value + 1)

class Double(TransformationStrategy[int, int]):
    def transform(self, value: int) -> Response[int]:
        return Response(status=Status.OK, details="double", value=value * 2)

class Chained(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [Inc(), Double(), RangeValidationStrategy(10, 50)]

def main():
    ok = Chained(4)    # (4+1)*2 = 10 → OK
    bad = Chained(26)  # (26+1)*2 = 54 → out of range
    print("ok:", ok.status.name, ok.value)
    print("bad:", bad.status.name, bad.details, bad.value)

if __name__ == "__main__":
    main()
