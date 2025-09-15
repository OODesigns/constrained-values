"""
Example 22 — Unknown strategy handler
Returning a strategy that is neither transform nor validation → EXCEPTION status.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from constrained_values.value import PipeLineStrategy, ConstrainedValue

class Unknown(PipeLineStrategy):
    pass

class UsesUnknown(ConstrainedValue[int]):
    def get_strategies(self):
        return [Unknown()]

def main():
    x = UsesUnknown(5)
    print("status:", x.status.name)
    print("details:", x.details)

if __name__ == "__main__":
    main()
