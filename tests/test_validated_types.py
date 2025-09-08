import unittest
from validated_value.status import Status
from validated_value.validated_types import EnumValidatedValue, RangeValidatedValue

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

if __name__ == '__main__':
    unittest.main()
