import typing
import unittest
from dataclasses import FrozenInstanceError

from constrained_values import Response, Status, T


class TestResponseOptionalSemantics(unittest.TestCase):
    def test_response_allows_none_value_on_exception(self):
        # Response.value is Optional[T], so None is valid when an error occurs.
        resp = Response[int](status=Status.EXCEPTION, details="boom", value=None)
        self.assertEqual(resp.status, Status.EXCEPTION)
        self.assertIsNone(resp.value)
        self.assertEqual(resp.details, "boom")

    # noinspection PyDataclass
    def test_response_is_frozen_dataclass(self):
        resp = Response[str](status=Status.OK, details="ok", value="hello")
        with self.assertRaises(FrozenInstanceError):
            resp.details = "mutated"  # frozen dataclass should prevent mutation

    def test_response_ok_holds_typed_value(self):
        resp = Response[int](status=Status.OK, details="fine", value=123)
        self.assertEqual(resp.status, Status.OK)
        self.assertEqual(resp.value, 123)

    def test_response_type_annotation_is_optional_in_original(self):
        # Inspect the annotations of Response
        hints = typing.get_type_hints(Response)
        self.assertEqual(hints["value"], typing.Optional[T])

    def test_response_accepts_none_value_at_runtime(self):
        # Even though type hint says T, we can pass None at runtime
        resp = Response(status=Status.EXCEPTION, details="bad", value=None)
        self.assertIsNone(resp.value)  # works fine at runtime


