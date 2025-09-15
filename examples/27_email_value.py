"""
Example 27 — Email value
Trim, lower, and validate a simple email pattern (non-exhaustive).
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import re
from typing import List
from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

class TrimLower(TransformationStrategy[str, str]):
    def transform(self, value: str) -> Response[str]:
        return Response(Status.OK, "normalize", value.strip().lower())

class Email(ConstrainedValue[str]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [TypeValidationStrategy(str), TrimLower()]

    def __bool__(self) -> bool:
        return self.ok and bool(EMAIL_RE.match(self.value))

def main():
    e1 = Email("  Alice@Example.com ")
    print("e1:", bool(e1), e1.value)
    e2 = Email("bad@@example")
    print("e2:", bool(e2), e2.value)

if __name__ == "__main__":
    main()
