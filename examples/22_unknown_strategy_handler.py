"""
Example 22 — Unknown strategy handler
Returning a strategy that is neither transform nor validation → EXCEPTION status.
"""
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
