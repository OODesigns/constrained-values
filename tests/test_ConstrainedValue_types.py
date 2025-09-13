import unittest
from decimal import Decimal
from fractions import Fraction

from validated_value.status import Status
from validated_value.ConstrainedValue_types import ConstrainedEnumValue, ConstrainedRangeValue

class TestEnumValidatedValue(unittest.TestCase):
    def test_enum_validated_value(self):
        valid_values = [Status.OK, Status.EXCEPTION]
        enum_val = ConstrainedEnumValue(Status.OK, Status, valid_values)

        self.assertEqual(enum_val.status, Status.OK, "Status should be OK after validation")
        self.assertIsNotNone(enum_val.value, "Validated value should not be None")
        self.assertEqual(enum_val.value, Status.OK, "Enum value should be OK")

    def test_enum_invalid_value(self):
        valid_values = [Status.OK, Status.EXCEPTION]
        invalid_val = ConstrainedEnumValue('Invalid', Status, valid_values)

        self.assertEqual(invalid_val.status, Status.EXCEPTION, "Status should be EXCEPTION after invalid input")
        self.assertIsNone(invalid_val.value, "Value should be None when validation fails")

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
        try:
            rv = ConstrainedRangeValue("5", 1, 10)
        except TypeError:
            self.fail("Value must be one of 'int',got 'str'")

        self.assertEqual(rv.status, Status.EXCEPTION)


    def test_enum_validation_reports_type_before_membership(self):
        rv = ConstrainedEnumValue(42, str, ["a", "b"])
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
        e = ConstrainedEnumValue(5, int, [3, 5, 7])
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
        e = ConstrainedEnumValue(5, int, [3, 5, 7])
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
        e = ConstrainedEnumValue(5, int, [3, 5, 7])  # Status.OK
        self.assertEqual(repr(e), "ConstrainedEnumValue(_value=5, status=OK)")

    def test_repr_enum_invalid(self):
        e = ConstrainedEnumValue(4, int, [3, 5, 7])  # Status.EXCEPTION (4 not allowed)
        self.assertEqual(repr(e), "ConstrainedEnumValue(_value=None, status=EXCEPTION)")

    def test_repr_handles_none_value_when_ok(self):
        # Edge case: if you ever allow None as a valid value
        e = ConstrainedEnumValue(None, type(None), [None])  # Status.OK
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

if __name__ == '__main__':
    unittest.main()
