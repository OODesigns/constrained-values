<p>
  <a href="https://oodesigns.github.io/constrained-values/constrained_values.html">
    <img height="20" alt="Documentation" src="https://img.shields.io/badge/docs-latest-brightgreen.svg?logo=readthedocs&logoColor=white">
  </a>
  <a href="https://github.com/oodesigns/constrained-values/actions">
    <img height="20" alt="Build Status" src="https://github.com/oodesigns/constrained-values/actions/workflows/website.yml/badge.svg">
  </a>
  <a href="https://pypi.org/project/constrained-values/">
    <img height="20" alt="PyPI Version" src="https://img.shields.io/pypi/v/constrained-values.svg?logo=pypi&logoColor=white">
  </a>
  <img height="20" alt="Python Versions" src="https://img.shields.io/pypi/pyversions/constrained-values.svg">
  <a href="https://opensource.org/licenses/MIT">
    <img height="20" alt="License: MIT" src="https://img.shields.io/badge/license-MIT-blue.svg">
  </a>
</p>

# Constrained Values

A lightweight Python library for **creating type-safe, self-validating value objects** — transforming primitive data into meaningful, domain-aware objects with rich validation and transformation pipelines.

---

## 🧭 Philosophy: Beyond Primitive Types

In most codebases, we pass around raw values without context:

- Is `temperature = 25` Celsius or Fahrenheit?
- Is `spi_mode = 2` valid for this device?
- What does `-32768` mean again?

Primitive values lack **meaning**, **constraints**, and **domain intent**.  
This is *Primitive Obsession* — a subtle but pervasive design smell.

**Constrained Values** replaces primitives with expressive, validated objects that *cannot exist in an invalid state*.

📖 [**Full Documentation →**](https://oodesigns.github.io/constrained-values/constrained_values.html#the-philosophy-beyond-primitive-types)

---

## ✨ Features

- 🧩 **Rich Value Objects** – Replace primitives with expressive, validated domain objects.
- 🔗 **Composable Pipelines** – Chain multiple validation and transformation strategies.
- 🧠 **Built-in Validators** – Range checks, enums, type coercion, and more.
- ⚙️ **Custom Logic** – Easily extend with your own domain-specific rules.
- 🚦 **Clear Error Handling** – Track validation status and descriptive messages.
- 🧯 **Optional Exception Mode** – Enforce invariants by raising on invalid input.
- 🧾 **Type-Safety** – Each value enforces its canonical type at runtime.

---

## 🚀 Installation

```bash
pip install constrained-values
