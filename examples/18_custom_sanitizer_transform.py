"""
Example 18 — Custom sanitizer transform
Trim/lower a string before validation.
"""
from typing import List

from constrained_values import Response, Status, TypeValidationStrategy, EnumValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy


class Trim(TransformationStrategy[str, str]):
    def transform(self, value: str) -> Response[str]:
        return Response(status=Status.OK, details="trim", value=value.strip())

class Lower(TransformationStrategy[str, str]):
    def transform(self, value: str) -> Response[str]:
        return Response(status=Status.OK, details="lower", value=value.lower())

class CleanFruit(ConstrainedValue[str]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [Trim(), Lower(), TypeValidationStrategy(str), EnumValidationStrategy(("apple","pear","plum"))]

def main():
    x = CleanFruit("  Apple  ")
    y = CleanFruit(" Banana ")
    print("x:", x.status.name, x.value)
    print("y:", y.status.name, y.details)

if __name__ == "__main__":
    main()
