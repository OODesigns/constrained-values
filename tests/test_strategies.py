import unittest
from decimal import Decimal
from fractions import Fraction
from typing import List

from constrained_values.constants import DEFAULT_SUCCESS_MESSAGE
from constrained_values.status import Status
from constrained_values.constrained_value_types import ConstrainedEnumValue, ConstrainedRangeValue
from constrained_values.strategies import (
    RangeValidationStrategy, TypeValidationStrategy, SameTypeValidationStrategy, get_types,
    CoerceToType, FailValidationStrategy,
)
from constrained_values.response import Response
from constrained_values.value import ConstrainedValue, TransformationStrategy, PipeLineStrategy


class TestValidatedValueStrategies(unittest.TestCase):
    def test_enum_validated_value_strategies(self):
        enum_val = ConstrainedEnumValue(Status.OK, Status)

        # Test that EnumValidatedValue has specific strategies
        self.assertEqual(len(enum_val.get_strategies()), 3, "EnumValidatedValue should have 3 validation strategies")

        # Prove that EnumValidatedValue strategies are not shared with RangeValidatedValue
        range_val = ConstrainedRangeValue(15, 10, 20)
        self.assertNotEqual(enum_val.get_strategies(), range_val.get_strategies(), "EnumValidatedValue should not share strategies with RangeValidatedValue")

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
        self.assertEqual(response.details, "Value must be one of 'int', 'float', got 'str'")

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
        self.assertEqual(r.details, "Type mismatch: expected type 'float' of value 2.0 to match 'int' of value 1")

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

class TestGetTypes(unittest.TestCase):
    def test_accepts_single_type(self):
        self.assertEqual(get_types(int), (int,))

    def test_accepts_sequence_of_types(self):
        self.assertEqual(get_types([int, str]), (int, str))

    def test_raises_on_non_type_single(self):
        with self.assertRaises(TypeError):
            get_types("int")  # not a type object

    def test_raises_on_mixed_sequence(self):
        with self.assertRaises(TypeError):
            get_types([int, "str"])  # second element is not a type

class TestTypeValidationStrategyConstructors(unittest.TestCase):
    def test_single_type_int(self):
        # Accept a single type
        strat = TypeValidationStrategy(int)
        ok = strat.validate(5)
        bad = strat.validate("x")
        from constrained_values.status import Status
        self.assertEqual(ok.status, Status.OK)
        self.assertEqual(bad.status, Status.EXCEPTION)
        # valid_types normalized to a tuple
        self.assertEqual(strat.valid_types, (int,))

    def test_multiple_types_list(self):
        # Accept a list of types
        strat = TypeValidationStrategy([int, float])
        from constrained_values.status import Status
        self.assertEqual(strat.validate(3.14).status, Status.OK)
        self.assertEqual(strat.validate(7).status, Status.OK)
        self.assertEqual(strat.validate("nope").status, Status.EXCEPTION)
        # normalized
        self.assertEqual(strat.valid_types, (int, float))

    def test_multiple_types_tuple(self):
        # Accept a tuple of types
        strat = TypeValidationStrategy((bytes, bytearray))
        from constrained_values.status import Status
        self.assertEqual(strat.validate(bytearray(b"a")).status, Status.OK)
        self.assertEqual(strat.validate(1).status, Status.EXCEPTION)
        # normalized
        self.assertEqual(strat.valid_types, (bytes, bytearray))

class TestCoerceToType(unittest.TestCase):
    def test_pass_through_when_already_target_float(self):
        r = CoerceToType(float).transform(1.25)
        self.assertEqual(r.status, Status.OK)
        self.assertIsInstance(r.value, float)
        self.assertEqual(r.value, 1.25)

    def test_int_to_float(self):
        r = CoerceToType(float).transform(3)
        self.assertEqual(r.status, Status.OK)
        self.assertIsInstance(r.value, float)
        self.assertEqual(r.value, 3.0)

    def test_int_to_decimal(self):
        r = CoerceToType(Decimal).transform(3)
        self.assertEqual(r.status, Status.OK)
        self.assertIs(type(r.value), Decimal)
        self.assertEqual(r.value, Decimal(3))

    def test_float_to_decimal_avoids_binary_fp_artifacts(self):
        # Uses Decimal(str(value)) per your implementation
        r = CoerceToType(Decimal).transform(0.1)
        self.assertEqual(r.status, Status.OK)
        self.assertEqual(r.value, Decimal("0.1"))

    def test_int_to_fraction(self):
        r = CoerceToType(Fraction).transform(2)
        self.assertEqual(r.status, Status.OK)
        self.assertIs(type(r.value), Fraction)
        self.assertEqual(r.value, Fraction(2, 1))

    def test_generic_constructor_fallback_str_to_complex(self):
        r = CoerceToType(complex).transform("3")
        self.assertEqual(r.status, Status.OK)
        self.assertEqual(r.value, complex(3))

    def test_un_coercible_yields_exception_response(self):
        class Weird:
            pass

        r = CoerceToType(int).transform(Weird())  # int(Weird()) -> TypeError
        self.assertEqual(r.status, Status.EXCEPTION)
        self.assertIsNone(r.value)

class TestFailValidationStrategy(unittest.TestCase):
    def test_fail_validation_returns_exception_status(self):
        s = FailValidationStrategy("boom")
        r = s.validate("anything")
        self.assertEqual(r.status, Status.EXCEPTION)
        self.assertEqual(r.details, "boom")

    def test_fail_validation_in_pipeline_short_circuits_and_sets_details(self):
        class AlwaysFails(ConstrainedValue[int]):
            def get_strategies(self) -> List[PipeLineStrategy]:
                return [FailValidationStrategy("nope")]
        x = AlwaysFails(123)
        self.assertEqual(x.status, Status.EXCEPTION)
        self.assertEqual(x.details, "nope")
        self.assertIsNone(x.value)

    def test_transform_then_fail_validation_still_fails(self):
        class Inc(TransformationStrategy):
            def transform(self, value):
                return Response(status=Status.OK, details="inc", value=value + 1)

        class TransformThenFail(ConstrainedValue[int]):
            def get_strategies(self) -> List[PipeLineStrategy]:
                return [Inc(), FailValidationStrategy("blocked")]
        x = TransformThenFail(10)
        self.assertEqual(x.status, Status.EXCEPTION)
        self.assertEqual(x.details, "blocked")
        # value should be None because pipeline failed
        self.assertIsNone(x.value)

class TestRangeValidationStrategyBounds(unittest.TestCase):
    def test_below_low_returns_exception_and_message(self):
        s = RangeValidationStrategy(10, 20)
        r = s.validate(9)
        self.assertEqual(r.status, Status.EXCEPTION)
        self.assertEqual(r.details, "Value must be greater than or equal to 10, got 9")

    def test_above_high_returns_exception_and_message(self):
        s = RangeValidationStrategy(10, 20)
        r = s.validate(21)
        self.assertEqual(r.status, Status.EXCEPTION)
        self.assertEqual(r.details, "Value must be less than or equal to 20, got 21")

    def test_edges_are_ok(self):
        s = RangeValidationStrategy(10, 20)
        self.assertEqual(s.validate(10).status, Status.OK)
        self.assertEqual(s.validate(20).status, Status.OK)
