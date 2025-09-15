import unittest
from decimal import Decimal
from enum import Enum
from fractions import Fraction

from constrained_values import Response
from constrained_values.status import Status
from constrained_values.constrained_value_types import ConstrainedEnumValue, ConstrainedRangeValue, StrictConstrainedValue
from constrained_values.strategies import FailValidationStrategy
from constrained_values.value import TransformationStrategy

# noinspection DuplicatedCode
class TestRangeValidatedValue(unittest.TestCase):
    def test_range_validated_value(self):
        range_val = ConstrainedRangeValue(15, 10, 20)

        self.assertEqual(range_val.status, Status.OK, "Status should be OK after valid input")
        self.assertEqual(range_val.value, 15, "Value should be 15")

    def test_range_invalid_value(self):
        range_val = ConstrainedRangeValue(25, 10, 20)

        self.assertEqual(range_val.status, Status.EXCEPTION, "Status should be EXCEPTION after invalid input")
        self.assertIsNone(range_val.value, "Value should be None when validation fails")

    def test_run_validations_references_correct_strategies(self):
        valid_values = [Status.OK, Status.EXCEPTION]

        # EnumValidatedValue should use EnumValidationStrategy and TypeValidationStrategy
        enum_val = ConstrainedEnumValue(Status.OK, Status, valid_values)
        enum_result = enum_val._run_pipeline(Status.OK, "validation successful")
        self.assertEqual(enum_result.status, Status.OK, "EnumValidatedValue should pass validation with correct enum")
        self.assertEqual(enum_result.details, "validation successful", "EnumValidatedValue should pass all validations")

        # RangeValidatedValue should use RangeValidationStrategy and TypeValidationStrategy
        range_val = ConstrainedRangeValue(15, 10, 20)
        range_result = range_val._run_pipeline(15, "validation successful")
        self.assertEqual(range_result.status, Status.OK, "RangeValidatedValue should pass validation with correct range")
        self.assertEqual(range_result.details, "validation successful", "RangeValidatedValue should pass all validations")

class TestTypeChecksAreInCorrectOrder(unittest.TestCase):
    def test_range_validation_checks_type_before_range(self):
        """
        Desired: type is validated BEFORE range checks.
        - Should NOT raise a raw TypeError when value is non-comparable (e.g., str vs int).
        - Should return a Response with Status.EXCEPTION and a clear type message.
        """
        rv = ConstrainedRangeValue("5", 1, 10)
        self.assertEqual(rv.status, Status.EXCEPTION)


    def test_enum_validation_reports_type_before_membership(self):
        rv = ConstrainedEnumValue(42, ["a", "b"])
        self.assertEqual(rv.status, Status.EXCEPTION)
        self.assertEqual(rv.details, "Value must be one of 'str', got 'int'")


# noinspection DuplicatedCode
class TestValidatedValueOrderingPreFix(unittest.TestCase):
    def test_ordering_across_statuses_should_raise(self):
        ok = ConstrainedRangeValue(5, 1, 10)
        bad = ConstrainedRangeValue("5", 1, 10)
        self.assertEqual(ok.status, Status.OK)
        self.assertEqual(bad.status, Status.EXCEPTION)

        with self.assertRaises(ValueError):
            _ = ok < bad
        with self.assertRaises(ValueError):
            _ = bad < ok
        with self.assertRaises(ValueError):
            _ = ok <= bad
        with self.assertRaises(ValueError):
            _ = bad <= ok

    def test_ordering_across_validated_classes_should_raise(self):
        r = ConstrainedRangeValue(5, 1, 10)
        e = ConstrainedEnumValue(5, [3, 5, 7])
        self.assertEqual(r.status, Status.OK)
        self.assertEqual(e.status, Status.OK)

        # Desired: ordering across different ValidatedValue classes should raise
        with self.assertRaises(TypeError):
            _ = r < e
        with self.assertRaises(TypeError):
            _ = e < r
        with self.assertRaises(TypeError):
            _ = r <= e
        with self.assertRaises(TypeError):
            _ = e <= r

class TestValidatedValueErrorsAndMessages(unittest.TestCase):
    def test_ordering_value_error_message_exact(self):
        ok = ConstrainedRangeValue(5, 1, 10)
        bad = ConstrainedRangeValue("5", 1, 10)
        self.assertEqual(bad.status, Status.EXCEPTION)

        with self.assertRaises(ValueError) as ctx:
            _ = ok < bad
        self.assertIn('ConstrainedRangeValue: cannot compare invalid values', str(ctx.exception))

        with self.assertRaises(ValueError) as ctx2:
            _ = bad <= ok
        self.assertIn('ConstrainedRangeValue: cannot compare invalid values', str(ctx2.exception))

class TestValidatedValueEqualitySemantics(unittest.TestCase):
    def test_equality_false_when_either_invalid(self):
        ok = ConstrainedRangeValue(5, 1, 10)
        bad = ConstrainedRangeValue("5", 1, 10)
        self.assertEqual(ok.status, Status.OK)
        self.assertEqual(bad.status, Status.EXCEPTION)

        self.assertNotEqual(ok, bad)
        self.assertNotEqual(bad, ok)

    def test_cross_class_equality_is_false(self):
        r = ConstrainedRangeValue(5, 1, 10)
        e = ConstrainedEnumValue(5, [3, 5, 7])
        self.assertEqual(r.status, Status.OK)
        self.assertEqual(e.status, Status.OK)

        self.assertNotEqual(r, e)
        self.assertNotEqual(e, r)

class TestValidatedValueSortingBehaviour(unittest.TestCase):
    def test_sorting_list_with_invalid_raises_value_error(self):
        a = ConstrainedRangeValue(3, 1, 10)       # OK
        b = ConstrainedRangeValue(7, 1, 10)       # OK
        bad = ConstrainedRangeValue("x", 1, 10)   # EXCEPTION

        items = [b, bad, a]
        with self.assertRaises(ValueError):
            items.sort()

class TestValidatedValueRepr(unittest.TestCase):
    def test_repr_range_valid_ok(self):
        v = ConstrainedRangeValue(5, 1, 10)  # Status.OK
        self.assertEqual(repr(v), "ConstrainedRangeValue(_value=5, status=OK)")

    def test_repr_range_invalid_preserves_raw_value_and_status(self):
        v = ConstrainedRangeValue("5", 1, 10)  # Status.EXCEPTION
        # Note the quotes around  '5' because of !r
        self.assertEqual(repr(v), "ConstrainedRangeValue(_value=None, status=EXCEPTION)")

    def test_repr_enum_valid_ok(self):
        e = ConstrainedEnumValue(5, [3, 5, 7])  # Status.OK
        self.assertEqual(repr(e), "ConstrainedEnumValue(_value=5, status=OK)")

    def test_repr_enum_invalid(self):
        e = ConstrainedEnumValue(4, [3, 5, 7])  # Status.EXCEPTION (4 not allowed)
        self.assertEqual(repr(e), "ConstrainedEnumValue(_value=None, status=EXCEPTION)")

    def test_repr_handles_none_value_when_ok(self):
        # Edge case: if you ever allow None as a valid value
        e = ConstrainedEnumValue(None, [None])  # Status.OK
        self.assertEqual(repr(e), "ConstrainedEnumValue(_value=None, status=OK)")

class TestRangeTypes(unittest.TestCase):
    def test_bounds_type_must_match_making_sure_first_test(self):
        bad = ConstrainedRangeValue(5, 10, "100")
        self.assertEqual(bad.status, Status.EXCEPTION)
        self.assertEqual(bad.details, "Type mismatch: expected type 'str' of value 100 to match 'int' of value 10")

class TestConstrainedRangeValueWithCoercion(unittest.TestCase):
    # --- integration-style tests exercising the CRV pipeline with CoerceToType(type(low_value)) ---

    def test_int_value_with_float_bounds_is_coerced_to_float(self):
        cv = ConstrainedRangeValue(3, 0.0, 10.0)  # int with float bounds
        self.assertEqual(cv.status, Status.OK)
        self.assertIsInstance(cv.value, float)
        self.assertEqual(cv.value, 3.0)

    def test_int_value_with_decimal_bounds_is_coerced_to_decimal(self):
        # Note: by design, TypeValidationStrategy for Decimal bounds typically allows (int, Decimal), not float
        cv = ConstrainedRangeValue(3, Decimal("0"), Decimal("10"))
        self.assertEqual(cv.status, Status.OK)
        self.assertIs(type(cv.value), Decimal)
        self.assertEqual(cv.value, Decimal(3))

    def test_int_value_with_fraction_bounds_is_coerced_to_fraction(self):
        cv = ConstrainedRangeValue(1, Fraction(0, 1), Fraction(3, 2))
        self.assertEqual(cv.status, Status.OK)
        self.assertIs(type(cv.value), Fraction)
        self.assertEqual(cv.value, Fraction(1, 1))

class DataOrder(Enum):
    MSB = True
    LSB = False


class Mixed(Enum):
    A = "a"
    B = "b"

class TestConstrainedEnumValueNewAPI(unittest.TestCase):
    def test_accepts_enum_class_and_underlying_values(self):
        # Using Enum class: should accept underlying values directly
        cv = ConstrainedEnumValue(True, DataOrder)
        self.assertEqual(cv.status, Status.OK)
        self.assertIs(cv.value, True)

        cv2 = ConstrainedEnumValue(False, DataOrder)
        self.assertEqual(cv2.status, Status.OK)
        self.assertIs(cv2.value, False)

    def test_accepts_enum_members_and_normalizes_to_underlying(self):
        # Using Enum class: should accept enum members and normalize to .value
        cv = ConstrainedEnumValue(DataOrder.MSB, DataOrder)
        self.assertEqual(cv.status, Status.OK)
        self.assertIs(cv.value, True)

        cv2 = ConstrainedEnumValue(DataOrder.LSB, DataOrder)
        self.assertEqual(cv2.status, Status.OK)
        self.assertIs(cv2.value, False)

    def test_rejects_integers_even_when_bool_is_expected(self):
        # Exact type check: 1/0 are ints, not bools
        bad1 = ConstrainedEnumValue(1, DataOrder)
        bad0 = ConstrainedEnumValue(0, DataOrder)
        self.assertEqual(bad1.status, Status.EXCEPTION)
        self.assertEqual(bad0.status, Status.EXCEPTION)

    def test_sequence_of_enum_members_is_supported(self):
        # Passing a *sequence of enum members* should behave like passing the Enum class
        allowed = [Mixed.A, Mixed.B]
        cv = ConstrainedEnumValue(Mixed.A, allowed)      # member accepted, normalized to 'a'
        self.assertEqual(cv.status, Status.OK)
        self.assertEqual(cv.value, "a")

        cv2 = ConstrainedEnumValue("b", allowed)         # underlying value also accepted
        self.assertEqual(cv2.status, Status.OK)
        self.assertEqual(cv2.value, "b")

        bad = ConstrainedEnumValue("c", allowed)         # not in allowed
        self.assertEqual(bad.status, Status.EXCEPTION)

    def test_empty_enum_or_empty_sequence_raises_configuration_error(self):
        class Empty(Enum):
            pass

        bad = ConstrainedEnumValue(True, Empty)
        self.assertEqual(bad.status, Status.EXCEPTION)

        bad = ConstrainedEnumValue("x", [])
        self.assertEqual(bad.status, Status.EXCEPTION)

class _EmptyEnum(Enum):
    pass

class _Color(Enum):
    RED = "r"
    BLUE = "b"

class TestConstrainedEnumValueNoThrows(unittest.TestCase):
    def test_empty_enum_yields_exception_status(self):
        cv = ConstrainedEnumValue("anything", _EmptyEnum)
        self.assertEqual(cv.status, Status.EXCEPTION)
        self.assertIn("no members", cv.details.lower())

    def test_empty_sequence_yields_exception_status(self):
        cv = ConstrainedEnumValue("x", [])
        self.assertEqual(cv.status, Status.EXCEPTION)
        self.assertIn("non-empty", cv.details.lower())

    def test_sequence_of_enum_members_supported_and_normalized(self):
        allowed = [_Color.RED, _Color.BLUE]  # members
        cv = ConstrainedEnumValue(_Color.RED, allowed)
        self.assertEqual(cv.status, Status.OK)
        self.assertEqual(cv.value, "r")  # normalized to underlying value

        cv2 = ConstrainedEnumValue("b", allowed)  # underlying ok too
        self.assertEqual(cv2.status, Status.OK)
        self.assertEqual(cv2.value, "b")

    def test_exact_type_is_enforced(self):
        # boolean example: ints are not accepted when underlying is bool
        class MyBool(Enum):
            T = True
            F = False
        bad = ConstrainedEnumValue(1, MyBool)
        self.assertEqual(bad.status, Status.EXCEPTION)

class TestConstrainedEnumValuePlainValues(unittest.TestCase):
    def test_plain_values_accepts_allowed_value(self):
        cv = ConstrainedEnumValue("a", ["a", "b"])
        self.assertEqual(cv.status, Status.OK)
        self.assertEqual(cv.value, "a")

    def test_plain_values_rejects_wrong_type(self):
        cv = ConstrainedEnumValue(42, ["a", "b"])
        self.assertEqual(cv.status, Status.EXCEPTION)

    def test_plain_values_rejects_value_not_in_allowed(self):
        cv = ConstrainedEnumValue("c", ["a", "b"])
        self.assertEqual(cv.status, Status.EXCEPTION)

    def test_plain_values_accepts_none_if_list_includes_none(self):
        cv = ConstrainedEnumValue(None, [None, "x"])
        self.assertEqual(cv.status, Status.OK)
        self.assertIsNone(cv.value)

class TestStrictValidatedValue(unittest.TestCase):
    def test_success_does_not_raise(self):
        class AlwaysOK(StrictConstrainedValue[int]):
            def get_strategies(self):
                return []  # no steps -> OK

        x = AlwaysOK(42)
        self.assertEqual(x.status, Status.OK)
        self.assertEqual(x.value, 42)

    def test_failure_raises_value_error_with_details(self):
        class AlwaysFail(StrictConstrainedValue[int]):
            def get_strategies(self):
                return [FailValidationStrategy("boom")]

        with self.assertRaises(ValueError) as ctx:
            AlwaysFail(123)

        msg = str(ctx.exception)
        self.assertIn("Failed Constraints for value - '123'", msg)
        self.assertIn("boom", msg)

    # noinspection DuplicatedCode
    def test_transform_then_fail_still_raises(self):
        class Inc(TransformationStrategy[int, int]):
            def transform(self, value: int) -> Response[int]:
                return Response(status=Status.OK, details="inc", value=value + 1)

        class TransformThenFail(StrictConstrainedValue[int]):
            def get_strategies(self):
                return [Inc(), FailValidationStrategy("blocked")]

        with self.assertRaises(ValueError) as ctx:
            TransformThenFail(10)

        self.assertIn("blocked", str(ctx.exception))

# noinspection DuplicatedCode
class TestConstrainedRangeValueInferValidTypes(unittest.TestCase):
    def test_int_returns_int_only(self):
        self.assertEqual(
            ConstrainedRangeValue.infer_valid_types_from_value(123),
            (int,),
        )

    def test_float_returns_int_and_float(self):
        self.assertEqual(
            ConstrainedRangeValue.infer_valid_types_from_value(1.5),
            (int, float),
        )

    def test_decimal_returns_int_and_decimal(self):
        self.assertEqual(
            ConstrainedRangeValue.infer_valid_types_from_value(Decimal("2")),
            (int, Decimal),
        )

    def test_fraction_returns_int_and_fraction(self):
        self.assertEqual(
            ConstrainedRangeValue.infer_valid_types_from_value(Fraction(1, 3)),
            (int, Fraction),
        )

    def test_default_exact_type_only_with_str(self):
        self.assertEqual(
            ConstrainedRangeValue.infer_valid_types_from_value("hello"),
            (str,),
        )

    def test_default_exact_type_only_with_custom_type(self):
        class Widget:
            pass
        self.assertEqual(
            ConstrainedRangeValue.infer_valid_types_from_value(Widget()),
            (Widget,),
        )


class AddOneTransform(TransformationStrategy[int, int]):
    """Toy strategy that always increments the value by 1."""
    def transform(self, value: int) -> Response[int]:
        return Response(Status.OK, "added one", value + 1)


class AlwaysFailTransform(TransformationStrategy[int, int]):
    """Toy strategy that always fails."""
    def transform(self, value: int) -> Response[int]:
        return Response(Status.EXCEPTION, "forced failure", None)


class CustomRangeValue(ConstrainedRangeValue[int]):
    """Subclass that inserts AddOneTransform in the pipeline."""
    def __init__(self, value: int, low: int, high: int):
        super().__init__(value, low, high)

    def get_custom_strategies(self):
        return [AddOneTransform()]


class FailingCustomRangeValue(ConstrainedRangeValue[int]):
    """Subclass that always fails during custom stage."""
    def __init__(self, value: int, low: int, high: int):
        super().__init__(value, low, high)

    def get_custom_strategies(self):
        return [AlwaysFailTransform()]


class TestConstrainedRangeValueCustomStrategies(unittest.TestCase):
    def test_custom_strategy_runs_before_range(self):
        # Base value 4 is incremented to 5, which is inside 0..10
        cv = CustomRangeValue(4, 0, 10)
        self.assertEqual(cv.status, Status.OK)
        self.assertEqual(cv.value, 5)

    def test_custom_strategy_can_force_failure(self):
        cv = FailingCustomRangeValue(4, 0, 10)
        self.assertEqual(cv.status, Status.EXCEPTION)
        self.assertIsNone(cv.value)
        self.assertIn("forced failure", cv.details)