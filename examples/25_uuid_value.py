"""
Example 25 — UUID parsing
Transform a string into uuid.UUID and validate version.
"""
import sys, pathlib
# Make repo root importable when running this file directly
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import uuid
from typing import List
from constrained_values import Response, Status, TypeValidationStrategy
from constrained_values.value import TransformationStrategy, ConstrainedValue, PipeLineStrategy

class ToUUID(TransformationStrategy[str, uuid.UUID]):
    def transform(self, value: str) -> Response[uuid.UUID]:
        try:
            return Response(Status.OK, "uuid", uuid.UUID(value))
        except Exception as e:
            return Response(Status.EXCEPTION, f"bad uuid: {e}", None)

class UUIDValue(ConstrainedValue[uuid.UUID]):
    def get_strategies(self) -> List[PipeLineStrategy]:
        return [TypeValidationStrategy(str), ToUUID()]

def main():
    x = UUIDValue("12345678-1234-5678-1234-567812345678")
    print("x:", x.status.name, x.value if x.ok else x.details)
    y = UUIDValue(str(uuid.uuid4()))
    print("y:", y.status.name, y.value.version if y.ok else y.details)

if __name__ == "__main__":
    main()
