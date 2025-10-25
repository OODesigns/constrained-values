"""Demonstrates how to use :class:`ConstrainedValue` types (like
:class:`EnumValue` and :class:`RangeValue`) inside a dataclass-style
configuration object to validate and normalize input data.

This example shows:
  * How to wrap constrained values within a dataclass.
  * How to perform field-by-field validation during initialization.
  * How to return a tuple of `(ok, result)` indicating success or errors.

Run directly:

    python examples/31_dataclass_integration.py

Expected output:

    OK: True WidgetConfig(name='Gizmo', color='green', slots=4)
    OK2: False {'color': "Value must be one of ('red', 'green', 'blue'), got purple",
         'slots': 'Value must be greater than or equal to 1, got 0'}
"""

import sys
import pathlib
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Tuple, Union

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import EnumValue, RangeValue


class Color(Enum):
    """An enumeration of valid widget colors."""
    RED = "red"
    GREEN = "green"
    BLUE = "blue"


@dataclass
class WidgetConfig:
    """A dataclass-like configuration object that uses constrained fields.

    Attributes:
        name: The name of the widget (unvalidated string).
        color: Validated color, as a :class:`Color` enum member.
        slots: Validated integer slot count between 1 and 16.
    """

    name: str
    color: Any
    slots: Any

    @classmethod
    def from_input(cls, name: str, color: Any, slots: Any) -> Tuple[bool, Union["WidgetConfig", Dict[str, str]]]:
        """Validate input and construct a `WidgetConfig` instance.

        Wraps input fields in :class:`ConstrainedValue` types to ensure
        they meet constraints before constructing the dataclass.

        Args:
            name: The widget's name (any string).
            color: The color input (enum value or string).
            slots: The slot count to validate (integer).

        Returns:
            Tuple[bool, Union[WidgetConfig, Dict[str, str]]]:
                * `(True, WidgetConfig)` if all validations succeed.
                * `(False, errors_dict)` if one or more validations fail.
        """
        cv_color = EnumValue(color, Color)
        cv_slots = RangeValue(slots, 1, 16)

        ok = cv_color.ok and cv_slots.ok
        if not ok:
            errors: Dict[str, str] = {}
            if not cv_color.ok:
                errors["color"] = cv_color.details
            if not cv_slots.ok:
                errors["slots"] = cv_slots.details
            return False, errors

        return True, cls(name=name, color=cv_color.value, slots=cv_slots.value)


def main() -> None:
    """Run the dataclass integration demonstration.

    Steps:
        1. Construct a valid configuration using `"Gizmo", "green", 4"`.
        2. Attempt to construct an invalid configuration with `"purple", 0"`.
        3. Print the success flag and resulting object or error dictionary.

    Prints:
        * `"OK: True WidgetConfig(name='Gizmo', color='green', slots=4)"`
        * `"OK2: False {'color': "Value must be one of ('red', 'green', 'blue'),
        *        got purple", 'slots': 'Value must be greater than or equal to 1, got 0'}"`
    """
    ok, res = WidgetConfig.from_input("Gizmo", "green", 4)
    print("OK:", ok, res)

    ok2, res2 = WidgetConfig.from_input("Oops", "purple", 0)
    print("OK2:", ok2, res2)


if __name__ == "__main__":
    main()
