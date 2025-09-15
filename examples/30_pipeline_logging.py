"""
Example 30 — Pipeline logging strategy
Collect per-step details to show what happened in the pipeline.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from typing import Any, List
from constrained_values import Response, Status
from constrained_values.value import TransformationStrategy, ConstrainedValue

class LogStep(TransformationStrategy[Any, Any]):
    def __init__(self, tag: str, fn):
        self.tag = tag
        self.fn = fn  # fn(value) -> new_value
        self.logs = []
    def transform(self, value: Any) -> Response[Any]:
        try:
            nv = self.fn(value)
            self.logs.append((self.tag, "OK", value, nv))
            return Response(Status.OK, self.tag, nv)
        except Exception as e:
            self.logs.append((self.tag, "EX", value, str(e)))
            return Response(Status.EXCEPTION, f"{self.tag}: {e}", None)

class LoggedValue(ConstrainedValue[Any]):
    __slots__ = ("_strategies",)
    def __init__(self, value):
        steps: List[LogStep] = [
            LogStep("strip", lambda s: s.strip()),
            LogStep("upper", lambda s: s.upper()),
            LogStep("suffix", lambda s: s + "_X"),
        ]
        # Base is frozen/slots; use object.__setattr__ and declare __slots__ locally
        object.__setattr__(self, "_strategies", steps)
        super().__init__(value)
    # Narrowed return type helps the type checker know about `.logs`
    def get_strategies(self) -> List[LogStep]:
        return self._strategies

def main():
    x = LoggedValue("  hi  ")
    for s in x.get_strategies():
        for entry in s.logs:
            print(entry)
    print("final:", x.status.name, x.value)

if __name__ == "__main__":
    main()