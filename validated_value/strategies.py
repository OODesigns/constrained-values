from validated_value import Response, Status, ValidationStrategy
from validated_value.constants import DEFAULT_SUCCESS_MESSAGE

class TypeValidationStrategy(ValidationStrategy):
    def __init__(self, valid_types):
        # If valid_types is a single type, convert it to a tuple
        if not isinstance(valid_types, (list, tuple)):
            valid_types = (valid_types,)
        self.valid_types = tuple(valid_types)  # Ensure it's always a tuple

    def validate(self, value) -> Response:
        if not isinstance(value, self.valid_types):
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_types}, got {type(value).__name__}",
                value=None
            )
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


class RangeValidationStrategy(ValidationStrategy):
    def __init__(self, low_value, high_value):
        self.low_value = low_value
        self.high_value = high_value

    def validate(self, value) -> Response:
        if value < self.low_value:
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be greater than or equal to {self.low_value}, got {value}",
                value=None
            )
        if value > self.high_value:
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be less than or equal to {self.high_value}, got {value}",
                value=None
            )
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)


class EnumValidationStrategy(ValidationStrategy):
    def __init__(self, valid_values):
        self.valid_values = valid_values

    def validate(self, value) -> Response:
        if value not in self.valid_values:
            return Response(
                status=Status.EXCEPTION,
                details=f"Value must be one of {self.valid_values}, got {value}",
                value=None
            )
        return Response(status=Status.OK, details=DEFAULT_SUCCESS_MESSAGE, value=value)
