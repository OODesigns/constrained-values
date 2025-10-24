"""
Example 29 — Record list validation
Validate a list of small records where each field uses a ConstrainedValue.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from enum import Enum
from typing import List, Dict, Any
from constrained_values import RangeValue, EnumValue

class Role(Enum):
    USER = "user"
    ADMIN = "admin"

def validate_records(rows: List[Dict[str, Any]]):
    out = []
    errs = []
    for i, row in enumerate(rows):
        uid = RangeValue(row.get("id"), 1, 10 ** 9)
        role = EnumValue(row.get("role"), Role)
        if uid.ok and role.ok:
            out.append({"id": uid.value, "role": role.value})
        else:
            errs.append((i, uid.details if not uid.ok else None, role.details if not role.ok else None))
    return out, errs

def main():
    rows = [{"id": 1, "role": "user"}, {"id": "x", "role": "owner"}, {"id": 2, "role": Role.ADMIN}]
    ok, bad = validate_records(rows)
    print("OK:", ok)
    print("ERRS:", bad)

if __name__ == "__main__":
    main()
