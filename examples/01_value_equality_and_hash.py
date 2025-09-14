"""
Example 01 — Value equality and hashing
Demonstrates equality between same-class Value instances, hashing, and dict/set behavior.
"""
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
