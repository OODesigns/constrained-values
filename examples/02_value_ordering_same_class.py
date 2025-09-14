"""
Example 02 — Value ordering in the same class
Ordering only compares same concrete Value class; reflected fallback not used.
"""
from constrained_values import Value

class BreakLtSame(Value[int]):
    def __init__(self, v: int): super().__init__(v)
    def __lt__(self, other):  # pragma: no cover (sentinel)
        raise RuntimeError("Reflected __lt__ should not be used")

def main():
    x = BreakLtSame(2)
    y = BreakLtSame(1)
    print("x > y:", x > y)  # uses __gt__ on Value; won't call reflected __lt__

if __name__ == "__main__":
    main()
