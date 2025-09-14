"""
Example 23 — App config validation (dict)
Validate a config dict (port range, log level enum, feature flag) using ConstrainedRangeValue and ConstrainedEnumValue.
"""
from enum import Enum
from typing import Dict, Tuple, Any

from constrained_values import ConstrainedRangeValue, Status, ConstrainedEnumValue


class LogLevel(Enum):
    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"

def validate_config(cfg: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
    errors = {}
    port = ConstrainedRangeValue(cfg.get("port"), 1024, 65535)
    if port.status != Status.OK:
        errors["port"] = port.details
    level = ConstrainedEnumValue(cfg.get("log_level"), LogLevel)
    if level.status != Status.OK:
        errors["log_level"] = level.details
    feature = ConstrainedEnumValue(cfg.get("feature_x"), [True, False])
    if feature.status != Status.OK:
        errors["feature_x"] = feature.details
    if errors:
        return False, errors
    return True, {"port": port.value, "log_level": level.value, "feature_x": feature.value}

def main():
    good = {"port": 8080, "log_level": "info", "feature_x": True}
    bad  = {"port": "8080", "log_level": "verbose", "feature_x": "yes"}
    print("GOOD:", validate_config(good))
    print("BAD :", validate_config(bad))

if __name__ == "__main__":
    main()
