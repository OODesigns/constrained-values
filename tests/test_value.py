import unittest
from dataclasses import FrozenInstanceError
from typing import Any, List

from constrained_values import Response, Status
from constrained_values.value import Value, ConstrainedValue, TransformationStrategy, PipeLineStrategy

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
    # noinspection PyDataclass
    def test_value_has_no_dict_and_blocks_dynamic_attrs(self):
        v = Value(123)
        # because of __slots__, Value should not have a __dict__
        self.assertFalse(hasattr(v, "__dict__"))

        # frozen dataclasses raise FrozenInstanceError (subclass of AttributeError) on any assignment;
        # on some Python builds, a TypeError can surface when slots are involved. Accept all.
        with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
            v.some_random_attr = "oops"

    def test_value_still_allows_access_to__value(self):
        v = Value(456)
        # internal attribute works as normal
        self.assertEqual(v._value, 456)

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

    def test_value_le_between_different_value_types_typeerror(self):
        """
        Desired: comparing different Value subclasses should NOT silently return False.
        Returning NotImplemented should let Python raise a TypeError for ordering ops.
        """
        v1 = Value(1)
        v2 = Value("x")
        with self.assertRaises(TypeError):
            _ = v1 <= v2

    def test_value_eq_with_incomparable_python_type_is_false(self):
        v = Value(1)
        self.assertNotEqual(v,"x")

class TestValueRepr(unittest.TestCase):
    def test_repr_int_value(self):
        v = Value(42)
        self.assertEqual(repr(v), "Value(42)")

    def test_repr_str_value(self):
        v = Value("hello")
        # note quotes around 'hello' because of !r
        self.assertEqual(repr(v), "Value('hello')")

    def test_repr_none_value(self):
        v = Value(None)
        self.assertEqual(repr(v), "Value(None)")

    def test_repr_list_value(self):
        v = Value([1, 2, 3])
        # lists use their own repr
        self.assertEqual(repr(v), "Value([1, 2, 3])")

    def test_repr_subclass_includes_subclass_name(self):
        class MyValue(Value[int]):
            pass
        v = MyValue(99)
        # __class__.__name__ should pick up subclass
        self.assertEqual(repr(v), "MyValue(99)")

class BreakLtSame(Value[int]):
    def __init__(self, v):
        super().__init__(v)
    def __lt__(self, other): # pragma: no cover
        # If Python fell back to reflected __lt__, we'd hit this and the test would fail.
        raise RuntimeError("Reflected __lt__ should not be used")

class BreakLeSame(Value[int]):
    def __init__(self, v):
        super().__init__(v)
    def __le__(self, other): # pragma: no cover
        raise RuntimeError("Reflected __le__ should not be used")

class TestValueOrdering(unittest.TestCase):
    def test_gt_direct_impl_same_class(self):
        """Ensure __gt__ is used directly and not via reflected __lt__ when classes match."""
        x = BreakLtSame(2)
        y = BreakLtSame(1)
        self.assertGreater(x , y)

    def test_ge_direct_impl_same_class(self):
        """Ensure __ge__ is used directly and not via reflected __le__ when classes match."""
        x = BreakLeSame(2)
        y = BreakLeSame(2)
        self.assertGreaterEqual(x , y)

class TestValueHashing(unittest.TestCase):
    def test_value_is_hashable(self):
        v = Value(10)
        h = hash(v)  # should not raise
        self.assertIsInstance(h, int)

    def test_equal_values_have_equal_hashes(self):
        a = Value(10)
        b = Value(10)
        self.assertEqual(a, b)
        self.assertEqual(hash(a), hash(b))

    def test_set_deduplicates_equal_values(self):
        a = Value(10)
        b = Value(10)
        s = {a, b}
        self.assertEqual(len(s), 1)

    def test_dict_uses_value_as_key(self):
        a1 = Value(10)
        a2 = Value(10)
        d = {a1: "first", a2: "second"}
        # keys are equal, so dict should have a single entry updated to 'second'
        self.assertEqual(len(d), 1)
        # Fetch using a fresh equal instance should work too
        self.assertEqual(d[Value(10)], "second")

class _PassThrough(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.OK, details="ok", value=value)

class ValidInt(ConstrainedValue[int]):
      def get_strategies(self):
         return [_PassThrough()]

class _Fail(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.EXCEPTION, details="boom", value=None)

class InvalidInt(ConstrainedValue[int]):
    def get_strategies(self):
        return [_Fail()]

class TestConstrainedValueValueHashing(unittest.TestCase):
    def test_valid_constrained_hash_and_dict_behavior(self):
        x1 = ValidInt(42)
        x2 = ValidInt(42)
        self.assertEqual(x1.status, Status.OK)
        self.assertEqual(x2.status, Status.OK)
        # equal & hashable
        self.assertEqual(x1, x2)
        self.assertIsInstance(hash(x1), int)
        self.assertEqual(hash(x1), hash(x2))
        # set/dict should deduplicate
        s = {x1, x2}
        self.assertEqual(len(s), 1)
        d = {x1: "a", x2: "b"}
        self.assertEqual(len(d), 1)
        self.assertEqual(d[ValidInt(42)], "b")

    def test_invalid_constrained_hash_and_dict_behavior(self):
        y1 = InvalidInt(42)
        y2 = InvalidInt(42)
        self.assertEqual(y1.status, Status.EXCEPTION)
        self.assertEqual(y2.status, Status.EXCEPTION)
        # invalid values are NOT equal to each other by design
        self.assertNotEqual(y1, y2)
        # but should still be hashable (policy choice: allow hashing even when invalid)
        h1 = hash(y1)
        h2 = hash(y2)
        self.assertIsInstance(h1, int)
        self.assertIsInstance(h2, int)
        # dict/set should keep them as separate keys
        s = {y1, y2}
        self.assertEqual(len(s), 2)
        d = {y1: "a", y2: "b"}
        self.assertEqual(len(d), 2)
        # a fresh InvalidInt shouldn't match an existing key
        with self.assertRaises(KeyError):
            _ = d[InvalidInt(42)]

class TestValueStrAndFormat(unittest.TestCase):
    def test_str_matches_underlying_int(self):
        v = Value(123)
        self.assertEqual(str(v), str(123))

    def test_str_matches_underlying_float(self):
        v = Value(3.14159)
        self.assertEqual(str(v), str(3.14159))

    def test_str_matches_underlying_str(self):
        v = Value("hello")
        self.assertEqual(str(v), "hello")

    def test_format_numeric_precision(self):
        v = Value(12.3456)
        self.assertEqual(format(v, ".2f"), format(12.3456, ".2f"))
        # f-string uses __format__ under the hood
        self.assertEqual(f"{v:.2f}", f"{12.3456:.2f}")

    def test_format_int_padding(self):
        v = Value(42)
        self.assertEqual(format(v, "04d"), format(42, "04d"))

    def test_format_string_alignment(self):
        v = Value("hi")
        self.assertEqual(format(v, "^5"), format("hi", "^5"))  # center align in width 5

class TestConstrainedValueBool(unittest.TestCase):
    def test_bool_true_when_ok(self):
        v = ValidInt(123)
        self.assertEqual(v.status, Status.OK)
        self.assertTrue(bool(v))

    def test_bool_false_when_exception(self):
        v = InvalidInt(123)
        self.assertEqual(v.status, Status.EXCEPTION)
        self.assertFalse(bool(v))

    def test_if_usage_filters_only_valid(self):
        ok = ValidInt(1)
        bad = InvalidInt(2)
        picked = [x for x in (ok, bad) if x]
        self.assertEqual(len(picked), 1)
        self.assertIs(picked[0], ok)

class TestValueImmutability(unittest.TestCase):
    # noinspection PyDataclass
    def test_assigning__value_raises_attribute_error(self):
        v = Value(100)
        with self.assertRaises(FrozenInstanceError):
            v._value = 200

    # noinspection PyDataclass
    def test_assigning_new_attr_raises_attribute_error(self):
        v = Value(1)
        with self.assertRaises(TypeError):
            v.some_new_attr = 5

    # noinspection PyDataclass
    def test_subclass_cannot_mutate_after_super_init(self):
        class SubValue(Value[int]):
            def __init__(self, x: int):
                super().__init__(x)  # freezes the instance

        s = SubValue(10)
        with self.assertRaises((FrozenInstanceError, AttributeError, TypeError)):
            s._value = 11
        self.assertEqual(s.value, 10)

class _PassThroughStr(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.OK, details="ok", value=value)

class _FailStr(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.EXCEPTION, details="boom", value=None)

class ValidIntStr(ConstrainedValue[int]):
    def get_strategies(self):
        return [_PassThroughStr()]

class InvalidIntStr(ConstrainedValue[int]):
    def get_strategies(self):
        return [_FailStr()]

class TestConstrainedValueStr(unittest.TestCase):
    def test_str_valid_prints_canonical_value(self):
        x = ValidIntStr(123)
        self.assertEqual(x.status, Status.OK)
        self.assertEqual(str(x), "123")

    def test_str_invalid_shows_marker_and_details(self):
        y = InvalidIntStr(7)
        self.assertEqual(y.status, Status.EXCEPTION)
        s = str(y)
        # Format should be: <invalid {ClassName}: {details}>
        self.assertTrue(s.startswith(f"<invalid {y.__class__.__name__}: "))
        self.assertIn("boom", s)  # the details from the failing transform
        self.assertTrue(s.endswith(">"))

class _PassThroughUnwrap(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.OK, details="ok", value=value)

class _FailUnwrap(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.EXCEPTION, details="boom unwrap", value=None)

class ValidIntUnwrap(ConstrainedValue[int]):
    def get_strategies(self):
        return [_PassThroughUnwrap()]

class InvalidIntUnwrap(ConstrainedValue[int]):
    def get_strategies(self):
        return [_FailUnwrap()]

class TestConstrainedValueUnwrap(unittest.TestCase):
    def test_unwrap_returns_value_when_valid(self):
        x = ValidIntUnwrap(456)
        self.assertEqual(x.status, Status.OK)
        self.assertEqual(x.unwrap(), 456)

    def test_unwrap_raises_with_details_when_invalid(self):
        y = InvalidIntUnwrap(999)
        self.assertEqual(y.status, Status.EXCEPTION)
        with self.assertRaisesRegex(ValueError, r"InvalidIntUnwrap.*boom unwrap"):
            y.unwrap()
class _PassThroughOk(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.OK, details="ok", value=value)

class _FailOk(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.EXCEPTION, details="boom ok", value=None)

class ValidIntOk(ConstrainedValue[int]):
    def get_strategies(self):
        return [_PassThroughOk()]

class InvalidIntOk(ConstrainedValue[int]):
    def get_strategies(self):
        return [_FailOk()]

class TestConstrainedValueOk(unittest.TestCase):
    def test_ok_true_when_status_ok(self):
        v = ValidIntOk(1)
        self.assertEqual(v.status, Status.OK)
        self.assertTrue(v.ok)

    def test_ok_false_when_exception(self):
        v = InvalidIntOk(1)
        self.assertEqual(v.status, Status.EXCEPTION)
        self.assertFalse(v.ok)

    def test_ok_matches_bool(self):
        good = ValidIntOk(5)
        bad = InvalidIntOk(5)
        self.assertEqual(good.ok, bool(good))
        self.assertEqual(bad.ok, bool(bad))
class _PassThroughFmt(TransformationStrategy):
    def transform(self, value):
        # Keep value as-is, succeed
        return Response(status=Status.OK, details="ok fmt", value=value)

class _FailFmt(TransformationStrategy):
    def transform(self, value):
        # Force failure so instance is invalid
        return Response(status=Status.EXCEPTION, details="boom fmt", value=None)

class ValidFloatFmt(ConstrainedValue[float]):
    def get_strategies(self):
        return [_PassThroughFmt()]

class InvalidFloatFmt(ConstrainedValue[float]):
    def get_strategies(self):
        return [_FailFmt()]

class TestConstrainedValueFormat(unittest.TestCase):
    def test_format_valid_delegates_to_underlying_value(self):
        v = ValidFloatFmt(12.3456)
        # Delegates to underlying value's __format__
        self.assertEqual(format(v, ".2f"), format(12.3456, ".2f"))
        self.assertEqual(f"{v:.3f}", f"{12.3456:.3f}")

    def test_format_invalid_returns_str_marker(self):
        iv = InvalidFloatFmt(99.9)
        self.assertEqual(iv.status, Status.EXCEPTION)
        # Formatting an invalid instance should return the same as str(), not "None"
        out1 = format(iv, ".2f")
        out2 = f"{iv}"
        self.assertEqual(out1, str(iv))
        self.assertEqual(out2, str(iv))
        self.assertTrue(out1.startswith(f"<invalid {iv.__class__.__name__}: "))
        self.assertIn("boom fmt", out1)
        self.assertTrue(out1.endswith(">"))

class _UnknownStrategy(PipeLineStrategy):
    """Deliberately not a ValidationStrategy or TransformationStrategy."""
    pass

class UsesUnknownStrategy(ConstrainedValue[int]):
    def get_strategies(self):
        # Returning a strategy with no handler should trigger an EXCEPTION response
        return [_UnknownStrategy()]

class TestConstrainedValueMissingStrategyHandler(unittest.TestCase):
    def test_pipeline_with_unknown_strategy_sets_exception_status_and_message(self):
        x = UsesUnknownStrategy(123)
        self.assertEqual(x.status, Status.EXCEPTION)
        self.assertIn("Missing strategy handler", x.details)
        # str() should use the invalid marker
        s = str(x)
        self.assertTrue(s.startswith(f"<invalid {x.__class__.__name__}: "))
        self.assertTrue(s.endswith(">"))
class AnotherPassThrough(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.OK, details="ok2", value=value)

class AnotherValidInt(ConstrainedValue[int]):
    def get_strategies(self):
        return [AnotherPassThrough()]

class AnotherFail(TransformationStrategy):
    def transform(self, value):
        return Response(status=Status.EXCEPTION, details="boom2", value=None)

class AnotherInvalidInt(ConstrainedValue[int]):
    def get_strategies(self):
        return [AnotherFail()]

class TestConstrainedValueSameStatus(unittest.TestCase):
    def test_same_status_true_when_both_ok(self):
        a = ValidInt(1)
        b = AnotherValidInt(2)
        self.assertTrue(a._same_status(b))

    def test_same_status_true_when_both_exception(self):
        a = InvalidInt(1)
        b = AnotherInvalidInt(2)
        self.assertTrue(a._same_status(b))

    def test_same_status_false_when_mixed(self):
        a = ValidInt(1)
        b = InvalidInt(2)
        self.assertFalse(a._same_status(b))

class _Fail2(TransformationStrategy):
    def transform(self, value: Any) -> Response:
        return Response(status=Status.EXCEPTION, details="boom2", value=None)

class ProbeComparable(ConstrainedValue[int]):
    def get_strategies(self) -> List:
        return [_PassThrough()]

    def probe_compare(self, other: "ProbeComparable", spy):
        # delegate to _is_comparing with provided spy callable
        return self._is_comparing(other, spy)

class BadComparable(ConstrainedValue[int]):
    def get_strategies(self) -> List:
        return [_Fail2()]

    def probe_compare(self, other: "ConstrainedValue[int]", spy):
        return self._is_comparing(other, spy)

class UnrelatedComparable(ConstrainedValue[int]):
    def get_strategies(self) -> List:
        return [_PassThrough()]

class Spy:
    def __init__(self):
        self.calls = []
    def __call__(self, o):
        self.calls.append(o)
        return True  # pretend comparator result

class TestIsComparing(unittest.TestCase):
    def test_invokes_func_when_same_class_and_both_valid(self):
        a = ProbeComparable(1)
        b = ProbeComparable(2)
        spy = Spy()
        out = a.probe_compare(b, spy)
        self.assertIs(out, True)
        self.assertEqual(spy.calls, [b])  # spy saw 'other'

    def test_raises_when_either_side_invalid_same_class(self):
        a = BadComparable(1)
        b = BadComparable(2)
        spy = Spy()
        with self.assertRaises(ValueError):
            a.probe_compare(b, spy)
        self.assertEqual(spy.calls, [])   # delegate not called

    def test_returns_notimplemented_when_different_classes(self):
        a = ProbeComparable(1)
        b = UnrelatedComparable(2)
        spy = Spy()
        out = a.probe_compare(b, spy)
        self.assertIs(out, NotImplemented)
        self.assertEqual(spy.calls, [])   # delegate not called
