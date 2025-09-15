"""
Example 31 — Dataclass wrapping ConstrainedValues
Build a dataclass-like config that aggregates ConstrainedValue fields and reports errors.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from dataclasses import dataclass
from enum import Enum
from typing import Any
from constrained_values import ConstrainedEnumValue, ConstrainedRangeValue

class Color(Enum):
    RED = "red"
    GREEN = "green"
    BLUE = "blue"

@dataclass
class WidgetConfig:
    name: str
    color: Any
    slots: Any

    @classmethod
    def from_input(cls, name: str, color: Any, slots: Any):
        cv_color = ConstrainedEnumValue(color, Color)
        cv_slots = ConstrainedRangeValue(slots, 1, 16)
        ok = cv_color.ok and cv_slots.ok
        errors = {}
        if not cv_color.ok: errors["color"] = cv_color.details
        if not cv_slots.ok: errors["slots"] = cv_slots.details
        return ok, errors if not ok else cls(name=name, color=cv_color.value, slots=cv_slots.value)

def main():
    ok, res = WidgetConfig.from_input("Gizmo", "green", 4)
    print("OK:", ok, res)
    ok2, res2 = WidgetConfig.from_input("Oops", "purple", 0)
    print("OK2:", ok2, res2)

if __name__ == "__main__":
    main()
