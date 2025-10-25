"""Validate a list of small records (dicts) where each field is checked using
constrained value types such as :class:`RangeValue` and :class:`EnumValue`.

This example shows:
  * How to iterate over a list of input records and validate each field.
  * How to collect normalized/typed outputs for valid rows.
  * How to collect structured error information for invalid rows.

Run directly:

    python examples/29_records_validation.py

Expected output:

    OK: [{'id': 1, 'role': 'user'}, {'id': 2, 'role': 'admin'}]
    ERRS: [(1, "Value must be one of 'int', got 'str'", "Value must be one of ('user', 'admin'), got owner")]
"""

import sys
import pathlib
from enum import Enum
from typing import List, Dict, Any, Tuple

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import RangeValue, EnumValue, Status


class Role(Enum):
    """Valid roles for records."""
    USER = "user"
    ADMIN = "admin"


def validate_records(rows: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Tuple[int, Any, Any]]]:
    """Validate a list of record dicts.

    Each row is expected to contain:
      * ``id`` — an integer in the inclusive range ``[1, 10**9]``.
      * ``role`` — one of :class:`Role` (``"user"`` or ``"admin"``), accepted
        either as the enum member or its underlying string value.

    For each row:
      * If both fields validate, a normalized dict ``{"id": int, "role": Role}``
        is appended to the OK list.
      * Otherwise, an error tuple ``(index, id_error, role_error)`` is appended
        to the error list. Missing errors are reported as ``None``.

    Args:
        rows: Input records to validate.

    Returns:
        Tuple[List[Dict[str, Any]], List[Tuple[int, Any, Any]]]:
            * First item — list of normalized, valid rows.
            * Second item — list of error tuples with the original row index and
              per-field error messages (or ``None`` if that field was OK).
    """
    out: List[Dict[str, Any]] = []
    errs: List[Tuple[int, Any, Any]] = []

    for i, row in enumerate(rows):
        uid = RangeValue(row.get("id"), 1, 10 ** 9)
        role = EnumValue(row.get("role"), Role)

        if uid.status == Status.OK and role.status == Status.OK:
            out.append({"id": uid.value, "role": role.value})
        else:
            errs.append(
                (
                    i,
                    uid.details if uid.status != Status.OK else None,
                    role.details if role.status != Status.OK else None,
                )
            )

    return out, errs


def main() -> None:
    """Run the record list validation demonstration.

    Creates a list with two valid rows and one invalid row, validates them,
    then prints the OK results and the collected error details.

    Prints:
        * ``OK: [...]`` — normalized rows.
        * ``ERRS: [...]`` — list of (index, id_error, role_error).
    """
    rows = [
        {"id": 1, "role": "user"},
        {"id": "x", "role": "owner"},
        {"id": 2, "role": Role.ADMIN},
    ]

    ok, bad = validate_records(rows)
    print("OK:", ok)
    print("ERRS:", bad)


if __name__ == "__main__":
    main()
