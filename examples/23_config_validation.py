"""Demonstrates validating a configuration dictionary using constrained value
types such as :class:`RangeValue` and :class:`EnumValue`.

This example shows:
  * How to validate multiple fields in a configuration dictionary.
  * How to enforce numeric ranges, enumerated string values, and boolean flags.
  * How to aggregate and return validation results in a structured form.

Run directly:

    python examples/23_config_validation.py

Expected output:

    GOOD: (True, {'port': 8080, 'log_level': 'info', 'feature_x': True})
    BAD : (False, {'port': "Value must be one of 'int', got 'str'", 'log_level':
               "Value must be one of ('debug', 'info', 'warn', 'error'), got verbose",
               'feature_x': "Value must be one of 'bool', got 'str'"})
"""

import sys
import pathlib
from enum import Enum
from typing import Dict, Tuple, Any

# ---------------------------------------------------------------------------
# Make repo root importable when running this file directly
# ---------------------------------------------------------------------------
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from constrained_values import RangeValue, Status, EnumValue


class LogLevel(Enum):
    """A simple enumeration representing valid log levels."""
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


def validate_config(cfg: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    """Validate a configuration dictionary.

    Uses constrained value types to validate each configuration field:

      * **port** — must be within `[1024, 65535]`
      * **log_level** — must match a member of :class:`LogLevel`
      * **feature_x** — must be a boolean (`True` or `False`)

    Args:
        cfg: The configuration dictionary to validate.

    Returns:
        Tuple[bool, Dict[str, Any]]: A tuple containing:
            * `True` and the validated config dict if all checks pass.
            * `False` and a dict of error messages if validation fails.
    """
    errors = {}

    port = RangeValue(cfg.get("port"), 1024, 65535)
    if port.status != Status.OK:
        errors["port"] = port.details

    level = EnumValue(cfg.get("log_level"), LogLevel)
    if level.status != Status.OK:
        errors["log_level"] = level.details

    feature = EnumValue(cfg.get("feature_x"), [True, False])
    if feature.status != Status.OK:
        errors["feature_x"] = feature.details

    if errors:
        return False, errors

    return True, {
        "port": port.value,
        "log_level": level.value,
        "feature_x": feature.value,
    }


def main() -> None:
    """Run the configuration validation demonstration.

    Creates two configuration dictionaries — one valid, one invalid — and
    validates them using :func:`validate_config`.

    Prints:
        * The validation result for a good configuration (True, normalized dict).
        * The validation result for a bad configuration (False, errors).
    """
    good = {"port": 8080, "log_level": "info", "feature_x": True}
    bad = {"port": "8080", "log_level": "verbose", "feature_x": "yes"}

    print("GOOD:", validate_config(good))
    print("BAD :", validate_config(bad))


if __name__ == "__main__":
    main()
