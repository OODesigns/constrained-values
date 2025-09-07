import unittest
from typing import List

from validated_value import Value, Status, EnumValidatedValue, EnumValidationStrategy, TypeValidationStrategy, \
    RangeValidationStrategy, RangeValidatedValue, Response, ValidatedValue, ValidationStrategy

class TestValue(unittest.TestCase):
    def test_value_equality(self):
        val1 = Value(10)
        val2 = Value(10)
        val3 = Value(20)

        self.assertEqual(val1, val2, "Values with the same content should be equal")
        self.assertNotEqual(val1, val3, "Values with different content should not be equal")

    def test_value_comparisons(self):
        val1 = Value(10)
        val2 = Value(20)

        self.assertLess(val1, val2, "val1 should be less than val2")
        self.assertLessEqual(val1, val2, "val1 should be less or equal to val2")
        self.assertLessEqual(val1, val1, "val1 should be less or equal to itself")
        self.assertGreater(val2, val1, "val2 should be greater than val1")
        self.assertGreaterEqual(val2, val1, "val2 should be greater or equal to val1")

class TestEnumValidatedValue(unittest.TestCase):
    def test_enum_validated_value(self):
        valid_values = [Status.OK, Status.EXCEPTION]
        enum_val = EnumValidatedValue(Status.OK, Status, valid_values)

        self.assertEqual(enum_val.status, Status.OK, "Status should be OK after validation")
        self.assertIsNotNone(enum_val.value, "Validated value should not be None")
        self.assertEqual(enum_val.value, Status.OK, "Enum value should be OK")

    def test_enum_invalid_value(self):
        valid_values = [Status.OK, Status.EXCEPTION]
        invalid_val = EnumValidatedValue('Invalid', Status, valid_values)

        self.assertEqual(invalid_val.status, Status.EXCEPTION, "Status should be EXCEPTION after invalid input")
        self.assertIsNone(invalid_val.value, "Value should be None when validation fails")

class TestRangeValidatedValue(unittest.TestCase):
    def test_range_validated_value(self):
        range_val = RangeValidatedValue(15, int, 10, 20)

        self.assertEqual(range_val.status, Status.OK, "Status should be OK after valid input")
        self.assertEqual(range_val.value, 15, "Value should be 15")

    def test_range_invalid_value(self):
        range_val = RangeValidatedValue(25, int, 10, 20)

        self.assertEqual(range_val.status, Status.EXCEPTION, "Status should be EXCEPTION after invalid input")
        self.assertIsNone(range_val.value, "Value should be None when validation fails")

class TestValidatedValueStrategies(unittest.TestCase):
    def test_enum_validated_value_strategies(self):
        valid_values = [Status.OK, Status.EXCEPTION]
        enum_val = EnumValidatedValue(Status.OK, Status, valid_values)

        # Test that EnumValidatedValue has specific strategies
        self.assertEqual(len(enum_val._strategies), 2, "EnumValidatedValue should have 2 validation strategies")
        self.assertIsInstance(enum_val._strategies[1], EnumValidationStrategy, "Second strategy should be EnumValidationStrategy")
        self.assertIsInstance(enum_val._strategies[0], TypeValidationStrategy, "First strategy should be TypeValidationStrategy")

        # Prove that EnumValidatedValue strategies are not shared with RangeValidatedValue
        range_val = RangeValidatedValue(15, int, 10, 20)
        self.assertNotEqual(enum_val._strategies, range_val._strategies, "EnumValidatedValue should not share strategies with RangeValidatedValue")

    def test_range_validated_value_strategies(self):
        range_val = RangeValidatedValue(15, int, 10, 20)

        # Test that RangeValidatedValue has specific strategies
        self.assertEqual(len(range_val._strategies), 2, "RangeValidatedValue should have 2 validation strategies")
        self.assertIsInstance(range_val._strategies[1], RangeValidationStrategy, "Second strategy should be RangeValidationStrategy")
        self.assertIsInstance(range_val._strategies[0], TypeValidationStrategy, "First strategy should be TypeValidationStrategy")

    def test_run_validations_references_correct_strategies(self):
        valid_values = [Status.OK, Status.EXCEPTION]

        # EnumValidatedValue should use EnumValidationStrategy and TypeValidationStrategy
        enum_val = EnumValidatedValue(Status.OK, Status, valid_values)
        enum_result = enum_val._run_validations(Status.OK, "validation successful")
        self.assertEqual(enum_result.status, Status.OK, "EnumValidatedValue should pass validation with correct enum")
        self.assertEqual(enum_result.details, "validation successful", "EnumValidatedValue should pass all validations")

        # RangeValidatedValue should use RangeValidationStrategy and TypeValidationStrategy
        range_val = RangeValidatedValue(15, int, 10, 20)
        range_result = range_val._run_validations(15, "validation successful")
        self.assertEqual(range_result.status, Status.OK, "RangeValidatedValue should pass validation with correct range")
        self.assertEqual(range_result.details, "validation successful", "RangeValidatedValue should pass all validations")

        # Confirm that run_validations uses the correct strategies for EnumValidatedValue and RangeValidatedValue
        self.assertNotEqual(enum_val._strategies, range_val._strategies, "EnumValidatedValue and RangeValidatedValue should not share strategies")

    # Test chaining between strategies in run_validations
    def test_run_validations_with_chaining(self):
        # Custom strategies to simulate chaining
        class IncrementStrategy:
            """ A simple strategy that increments the value by 1. """
            @staticmethod
            def validate(value):
                return Response(status=Status.OK, details="Incremented value", value=value + 1)

        class DoubleStrategy:
            """ A simple strategy that doubles the value. """
            @staticmethod
            def validate(value):
                return Response(status=Status.OK, details="Doubled value", value=value * 2)

        # Creating a custom validated value with chained strategies
        class ChainedValue(ValidatedValue):
            def get_strategies(self) -> List[ValidationStrategy]:
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
        self.assertEqual(response.value, 42)

        # Test invalid string value
        response = strategy.validate("string")
        self.assertEqual(response.status, Status.EXCEPTION)
        self.assertEqual(response.details, "Value must be one of (<class 'int'>,), got str")
        self.assertIsNone(response.value)

    def test_multiple_types_validation(self):
        # Test multiple types validation (int and float)
        strategy = TypeValidationStrategy([int, float])

        # Test valid int value
        response = strategy.validate(42)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")
        self.assertEqual(response.value, 42)

        # Test valid float value
        response = strategy.validate(42.0)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")
        self.assertEqual(response.value, 42.0)

        # Test invalid string value
        response = strategy.validate("string")
        self.assertEqual(response.status, Status.EXCEPTION)
        self.assertEqual(response.details, "Value must be one of (<class 'int'>, <class 'float'>), got str")
        self.assertIsNone(response.value)

    def test_single_type_as_list(self):
        # Test that a single type in a list works the same as passing it directly
        strategy = TypeValidationStrategy([int])

        # Test valid int value
        response = strategy.validate(422)
        self.assertEqual(response.status, Status.OK)
        self.assertEqual(response.details, "validation successful")
        self.assertEqual(response.value, 422)

        # Test invalid string value
        response = strategy.validate("string")
        self.assertEqual(response.status, Status.EXCEPTION)
        self.assertEqual(response.details, "Value must be one of (<class 'int'>,), got str")
        self.assertIsNone(response.value)

class TestTypeChecksAreInCorrectOrder(unittest.TestCase):
    def test_range_validation_checks_type_before_range(self):
        """
        Desired: type is validated BEFORE range checks.
        - Should NOT raise a raw TypeError when value is non-comparable (e.g., str vs int).
        - Should return a Response with Status.EXCEPTION and a clear type message.
        """
        try:
            rv = RangeValidatedValue("5", int, 1, 10)
        except TypeError:
            self.fail("Value must be one of (<class 'int'>,), got str")

        self.assertEqual(rv.status, Status.EXCEPTION)


    def test_enum_validation_reports_type_before_membership(self):
        """
        Desired: for EnumValidatedValue, type is validated BEFORE membership.
        - Wrong-type inputs should produce a type message,
          NOT a membership/allowed-values message dump.
        """
        try:
          rv = EnumValidatedValue(42, str, ["a", "b"])
        except TypeError:
          self.fail("Value must be one of (<class 'str'>,), got int")

        self.assertEqual(rv.status, Status.EXCEPTION)

class TestValueSlots(unittest.TestCase):
    def test_value_has_no_dict_and_blocks_dynamic_attrs(self):
        v = Value(123)
        # because of __slots__, Value should not have a __dict__
        self.assertFalse(hasattr(v, "__dict__"))

        # trying to set an attribute not in __slots__ should raise AttributeError
        with self.assertRaises(AttributeError):
            v.some_random_attr = "oops"

    def test_value_still_allows_access_to__value(self):
        v = Value(456)
        # internal attribute works as normal
        self.assertEqual(v._value, 456)

        # modifying _value directly should still work
        v._value = 789
        self.assertEqual(v._value, 789)

    def test_multiple_instances_do_not_share_state(self):
        v1 = Value(1)
        v2 = Value(2)
        self.assertEqual(v1._value, 1)
        self.assertEqual(v2._value, 2)


class TestExpectedBehaviourWhenComparing(unittest.TestCase):
    def test_value_lt_with_incomparable_python_type_raises_typeerror(self):
        """
        Desired: comparisons with unsupported RHS should return NotImplemented,
        allowing Python to raise TypeError for ordering ops.
        """
        v = Value(1)
        with self.assertRaises(TypeError):
          _ = v < "x"


    def test_value_lt_between_different_value_classes_raises_typeerror(self):
        """
        Desired: comparing different Value subclasses should NOT silently return False.
        Returning NotImplemented should let Python raise a TypeError for ordering ops.
        """
        class OtherValue(Value[int]):
            pass

        v1 = Value(1)
        v2 = OtherValue(1)
        with self.assertRaises(TypeError):
            _ = v1 < v2

    def test_value_le_between_different_value_classes_raises_typeerror(self):
        """
        Desired: comparing different Value subclasses should NOT silently return False.
        Returning NotImplemented should let Python raise a TypeError for ordering ops.
        """
        class OtherValue(Value[int]):
            pass

        v1 = Value(1)
        v2 = OtherValue(1)
        with self.assertRaises(TypeError):
            _ = v1 <= v2

    def test_value_le_with_incomparable_python_type_raises_typeerror(self):
        """
        Desired: comparisons with unsupported RHS should return NotImplemented,
        allowing Python to raise TypeError for ordering ops.
        """
        v = Value(1)
        with self.assertRaises(TypeError):
            _ = v <= "x"

    def test_value_eq_with_incomparable_python_type_is_false(self):
        v = Value(1)
        self.assertNotEqual(v,"x")


    if __name__ == '__main__':
        unittest.main()
