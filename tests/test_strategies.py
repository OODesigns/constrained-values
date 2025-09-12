import unittest
from typing import List

from validated_value.constants import DEFAULT_SUCCESS_MESSAGE
from validated_value.status import Status
from validated_value.ConstrainedValue_types import ConstrainedEnumValue, ConstrainedRangeValue
from validated_value.strategies import (
    EnumValidationStrategy, RangeValidationStrategy, TypeValidationStrategy, SameTypeValidationStrategy,
)
from validated_value.response import Response
from validated_value.value import ConstrainedValue, TransformationStrategy, PipeLineStrategy


class TestValidatedValueStrategies(unittest.TestCase):
    def test_enum_validated_value_strategies(self):
        valid_values = [Status.OK, Status.EXCEPTION]
        enum_val = ConstrainedEnumValue(Status.OK, Status, valid_values)

        # Test that EnumValidatedValue has specific strategies
        self.assertEqual(len(enum_val._strategies), 2, "EnumValidatedValue should have 2 validation strategies")
        self.assertIsInstance(enum_val._strategies[1], EnumValidationStrategy, "Second strategy should be EnumValidationStrategy")
        self.assertIsInstance(enum_val._strategies[0], TypeValidationStrategy, "First strategy should be TypeValidationStrategy")

        # Prove that EnumValidatedValue strategies are not shared with RangeValidatedValue
        range_val = ConstrainedRangeValue(15, 10, 20)
        self.assertNotEqual(enum_val._strategies, range_val._strategies, "EnumValidatedValue should not share strategies with RangeValidatedValue")

    # Test chaining between strategies in run_validations
    def test_run_validations_with_chaining(self):
        # Custom strategies to simulate chaining
        class IncrementStrategy(TransformationStrategy):
            """ A simple strategy that increments the value by 1. """
            def transform(self, value):
                return Response(status=Status.OK, details="Incremented value", value=value + 1)

        class DoubleStrategy(TransformationStrategy):
            """ A simple strategy that doubles the value. """
            def transform(self,value):
                return Response(status=Status.OK, details="Doubled value", value=value * 2)

        # Creating a custom validated value with chained strategies
        class ChainedValue(ConstrainedValue):
            def get_strategies(self) -> List[PipeLineStrategy]:
                return [
                    IncrementStrategy(),
                    DoubleStrategy(),
                    RangeValidationStrategy(10, 50)  # Ensure the final value falls in range
                ]

        # Test a value that should pass the chain
        result = ChainedValue(4)
        self.assertEqual(result.status, Status.OK, "Value should pass all validations after chaining")
        self.assertEqual(result.value, 10, "Value should be incremented and then doubled to 10")

        # Test a value that should fail the range validation after chaining
        result = ChainedValue(26)
        self.assertEqual(result.status, Status.EXCEPTION, "Value should fail range validation after chaining")
        self.assertIsNone(result.value, "Value should be None after failing validation")

class TestTypeValidationStrategy(unittest.TestCase):

    def test_single_type_validation(self):
        # Test single type validation (int)
        strategy = TypeValidationStrategy(int)

        # Test valid int value
        response = strategy.validate(42)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")

        # Test invalid string value
        response = strategy.validate("string")
        self.assertEqual(response.status, Status.EXCEPTION)
        self.assertEqual(response.details, "Value must be one of 'int', got 'str'")

    def test_multiple_types_validation(self):
        # Test multiple types validation (int and float)
        strategy = TypeValidationStrategy([int, float])

        # Test valid int value
        response = strategy.validate(42)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")

        # Test valid float value
        response = strategy.validate(42.0)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")

        # Test invalid string value
        response = strategy.validate("string")
        self.assertEqual(response.status, Status.EXCEPTION)
        self.assertEqual(response.details, "Value must be one of 'int','float', got 'str'")

    def test_single_type_as_list(self):
        # Test that a single type in a list works the same as passing it directly
        strategy = TypeValidationStrategy([int])

        # Test valid int value
        response = strategy.validate(422)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")

        # Test invalid string value
        response = strategy.validate("string")
        self.assertEqual(response.status, Status.EXCEPTION)
        self.assertEqual(response.details, "Value must be one of 'int', got 'str'")

class TestSameTypeValidationStrategy(unittest.TestCase):
    def test_same_type_ints_ok(self):
        """Both values are int → OK; value passes through unchanged."""
        s = SameTypeValidationStrategy(1, 10)
        r = s.validate(999)
        self.assertEqual(r.status, Status.OK)
        self.assertEqual(r.details, DEFAULT_SUCCESS_MESSAGE)

    def test_same_type_floats_ok(self):
        """Both values are float → OK."""
        s = SameTypeValidationStrategy(1.0, 2.0)
        r = s.validate("payload")
        self.assertEqual(r.status, Status.OK)

    def test_mismatched_int_vs_float_returns_exception(self):
        """
        int vs float → should NOT raise Python TypeError.
        Should return Response(Status.EXCEPTION) with a helpful message.
        """
        s = SameTypeValidationStrategy(1, 2.0)
        r = s.validate(None)
        self.assertEqual(r.status, Status.EXCEPTION)
        # Message should mention both type names in a human-friendly way.
        self.assertEqual(r.details, "value:1 must match Type of value:2.0, as type 'float'")

    def test_bool_vs_int_is_strict_and_fails(self):
        """
        bool is a subclass of int; strict same-type means this should fail.
        """
        s = SameTypeValidationStrategy(True, 1)
        r = s.validate(None)
        self.assertEqual(r.status, Status.EXCEPTION)

    def test_custom_class_and_subclass_fail_strict(self):
        """Subclass should NOT match base class under strict equality."""
        class A: ...
        class B(A): ...

        ok = SameTypeValidationStrategy(A(), A()).validate(0)
        self.assertEqual(ok.status, Status.OK)

        bad = SameTypeValidationStrategy(A(), B()).validate(0)
        self.assertEqual(bad.status, Status.EXCEPTION)

if __name__ == '__main__':
    unittest.main()
