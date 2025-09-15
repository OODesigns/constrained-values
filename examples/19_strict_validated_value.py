"""
Example 19 — StrictValidatedValue
Strict variant raises ValueError if pipeline fails.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import List
from constrained_values import StrictValidatedValue
from constrained_values.strategies import FailValidationStrategy


class AlwaysOK(StrictValidatedValue[int]):
    def get_strategies(self) -> List: return []

class AlwaysFail(StrictValidatedValue[int]):
    def get_strategies(self) -> List: return [FailValidationStrategy("boom")]

def main():
    x = AlwaysOK(7)
    print("AlwaysOK:", x.status.name, x.value)
    try:
        AlwaysFail(9)
    except ValueError as e:
        print("AlwaysFail raised:", e)

if __name__ == "__main__":
    main()
