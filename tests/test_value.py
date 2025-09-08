import unittest
from validated_value.value import Value

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
