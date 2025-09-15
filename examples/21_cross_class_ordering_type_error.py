"""
Example 21 — Cross-class ordering TypeError
Ordering across different ConstrainedValue subclasses returns NotImplemented → TypeError.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import List
from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class Pass(TransformationStrategy[int, int]):
    def transform(self, value: int) -> Response[int]: return Response(status=Status.OK, details="ok", value=value)

class A(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Pass()]

class B(ConstrainedValue[int]):
    def get_strategies(self) -> List[PipeLineStrategy]: return [Pass()]

def main():
    a, b = A(1), B(2)
    try:
        print("a < b →", a < b)
    except TypeError as e:
        print("TypeError (as designed):", e)

if __name__ == "__main__":
    main()
