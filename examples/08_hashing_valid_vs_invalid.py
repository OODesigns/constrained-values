"""
Example 08 — Hashing policy
Valid instances hash by (class, value); invalid by (class, status).
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import Any
from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue

class Pass(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]: return Response(status=Status.OK, details="ok", value=value)

class Fail(TransformationStrategy[Any, Any]):
    def transform(self, value: Any) -> Response[Any]: return Response(status=Status.EXCEPTION, details="boom", value=None)

class ValidInt(ConstrainedValue[int]):
    def get_strategies(self): return [Pass()]

class InvalidInt(ConstrainedValue[int]):
    def get_strategies(self): return [Fail()]

def main():
    a, b = ValidInt(42), ValidInt(42)
    print("equal valid hashes:", hash(a) == hash(b))
    s = {a, b}
    print("set size for valid duplicates (1):", len(s))

    x, y = InvalidInt(1), InvalidInt(1)
    print("invalid equal? (False):", x == y)
    print("both hashable:", isinstance(hash(x), int) and isinstance(hash(y), int))
    s2 = {x, y}
    print("set size for invalid values (2):", len(s2))

if __name__ == "__main__":
    main()
