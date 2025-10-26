[![Docs](https://img.shields.io/badge/docs-latest-brightgreen.svg?logo=readthedocs&logoColor=white)](https://OODesigns.github.io/constrained-values/constrained_values.html)
[![Build Status](https://github.com/oodesigns/constrained-values/actions/workflows/website.yml/badge.svg)](https://github.com/OODesigns/constrained-values/actions)
[![PyPI Version](https://img.shields.io/pypi/v/constrained-values.svg?logo=pypi&logoColor=white)](https://pypi.org/project/constrained-values/)
![Python Versions](https://img.shields.io/pypi/pyversions/constrained-values.svg)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

## Constrained Values

A lightweight Python library for **creating type-safe, self-validating value objects** — transforming primitive data into meaningful, domain-aware objects with rich validation and transformation pipelines.

---

## 🧭 Philosophy: Beyond Primitive Types

In most codebases, we pass around raw values without context:

- Is `temperature = 25` Celsius or Fahrenheit?
- Is `spi_mode = 2` valid for this device?
- What does `-32768` mean again?

Primitive values lack **meaning**, **constraints**, and **domain intent**.  
This is *Primitive Obsession* — a subtle but pervasive design smell.

**Constrained Values** replaces primitives with expressive, validated objects that make **validity explicit**.  
Each object carries its **status** (`OK` or `EXCEPTION`) and associated errors.  

By default, invalid values can exist safely and report their state — but if you want to enforce strict invariants, you can enable **exception mode** to raise immediately on invalid input.

📖 [**Full Documentation →**](https://oodesigns.github.io/constrained-values/constrained_values.html#the-philosophy-beyond-primitive-types)

---

## ✨ Features

- 🧩 **Rich Value Objects** – Replace primitives with expressive, validated domain objects.
- 🔗 **Composable Pipelines** – Chain multiple validation and transformation strategies.
- 🧠 **Built-in Validators** – Range checks, enums, type coercion, and more.
- ⚙️ **Custom Logic** – Easily extend with your own domain-specific rules.
- 🚦 **Clear Error Handling** – Track validation status and descriptive messages.
- 🧯 **Strict/Exception Mode (optional)** – By default, invalid values are reported non-destructively; enable strict mode to raise exceptions and enforce invariants at creation.
- 🧾 **Type-Safety** – Each value enforces its canonical type at runtime.

---

## 🚀 Installation

```bash
pip install constrained-values
```
## 💡 Quick Example

```python
from constrained_value_types import RangeValue, CoerceToType, RangeValidationStrategy
from response import Status

class Temperature(RangeValue):
    """Temperature constrained between 0 and 100°C."""
    def __init__(self, value):
        super().__init__(value, low_value=0, high_value=100)

# ✅ Valid temperature
t = Temperature(42)
print("Value:", t.value)        # 42
print("Status:", t.status.name) # OK
print("Details:", t.details)    # success message

# 🚫 Invalid temperature
t_invalid = Temperature(120)
print("Value:", t_invalid.value)   # None
print("Status:", t_invalid.status) # Status.EXCEPTION
print("Details:", t_invalid.details)  # Something like "out of range: expected 0 <= x <= 100"
```
## 🔥 Strict version
If you want the behavior where invalid input throws immediately, use the StrictValue mixin:
```python
from constrained_value_types import StrictValue, RangeValue

class StrictTemperature(RangeValue, StrictValue):
    """Same range constraint but raises if invalid."""
    def __init__(self, value):
        RangeValue.__init__(self, value, low_value=0, high_value=100)

# ✅ OK
StrictTemperature(42)

# 🚫 Raises ValueError
StrictTemperature(120)
```
