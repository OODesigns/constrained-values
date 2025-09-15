"""
Example 01 — Value equality and hashing
Demonstrates equality between same-class Value instances, hashing, and dict/set behavior.
"""
import sys, pathlib
# Make repo root importable when running this file directly
"""
__file__ → the path of the current file (e.g., tests/test_strategies.py).
.resolve() → turns it into an absolute, symlink-free path.
.parents[1] → go up two levels:
parents[0] = the file’s folder (e.g., .../tests)
parents[1] = the folder above that (e.g., your repo root)
str(...) → convert the Path to a string for sys.path.
sys.path.insert(0, ...) → prepend that directory to Python’s import search path, so import
"""
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from constrained_values import Value
def main():
    a = Value(10)
    b = Value(10)
    c = Value(20)
    print("a == b:", a == b)
    print("a == c:", a == c)
    print("hash(a) == hash(b):", hash(a) == hash(b))
    s = {a, b, c}
    print("set size (should be 2):", len(s))
    d = {a: "first", b: "second", c: "third"}
    print("dict size (should be 2):", len(d))
    print("dict[a] =", d[a])

if __name__ == "__main__":
    main()
