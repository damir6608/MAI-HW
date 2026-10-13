"""Order business scenarios and boundary conditions."""

import unittest
from datetime import date, datetime

from foodtech.orders import OrderItem, quote_order


class OrderTests(unittest.TestCase):
    """Verify the quote contract without network or clock dependencies."""

    def setUp(self) -> None:
        self.items = [OrderItem(90000, 2), OrderItem(110000, 1)]
        self.today = date(2026, 10, 12)
        self.delivery = date(2026, 10, 14)

    def quote(self, **overrides: object) -> object:
        """Apply an individual boundary input to the valid reference order."""
        inputs = dict(
            items=self.items, days=1, first_delivery=self.delivery,
            today=self.today, delivery_kopecks=15000,
        )
        inputs.update(overrides)
        return quote_order(**inputs)

    def test_one_day_total(self) -> None:
        result = self.quote()
        self.assertEqual(result.subtotal_kopecks, 290000)
        self.assertEqual(result.total_kopecks, 305000)

    def test_week_delivery_charged_once(self) -> None:
        result = self.quote(days=7)
        self.assertEqual(result.subtotal_kopecks, 2030000)
        self.assertEqual(result.delivery_kopecks, 15000)
        self.assertEqual(result.total_kopecks, 2045000)

    def test_delivery_boundary_two_days(self) -> None:
        self.assertEqual(self.quote().first_delivery, self.delivery)

    def test_delivery_one_day(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(first_delivery=date(2026, 10, 13))

    def test_delivery_in_past(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(first_delivery=date(2026, 10, 11))

    def test_month_boundary(self) -> None:
        result = self.quote(today=date(2026, 10, 31), first_delivery=date(2026, 11, 2))
        self.assertEqual(result.first_delivery, date(2026, 11, 2))

    def test_year_boundary(self) -> None:
        result = self.quote(today=date(2026, 12, 31), first_delivery=date(2027, 1, 2))
        self.assertEqual(result.first_delivery, date(2027, 1, 2))

    def test_upper_date_boundary(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(today=date.max, first_delivery=date.max)

    def test_empty_order(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(items=[])

    def test_invalid_duration(self) -> None:
        for days in (0, 2, 8, -1):
            with self.subTest(days=days), self.assertRaises(ValueError):
                self.quote(days=days)

    def test_boolean_duration(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(days=True)

    def test_float_duration(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(days=1.0)

    def test_negative_price(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(items=[OrderItem(-1, 1)])

    def test_zero_quantity(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(items=[OrderItem(100, 0)])

    def test_negative_quantity(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(items=[OrderItem(100, -1)])

    def test_boolean_quantity(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(items=[OrderItem(100, True)])

    def test_boolean_price(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(items=[OrderItem(True, 1)])

    def test_float_price(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(items=[OrderItem(1.5, 1)])

    def test_wrong_item(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(items=[{"price": 100}])

    def test_wrong_container(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(items=tuple(self.items))

    def test_wrong_date_type(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(first_delivery="2026-10-14")

    def test_datetime_rejected(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(today=datetime(2026, 10, 12))

    def test_negative_delivery(self) -> None:
        with self.assertRaises(ValueError):
            self.quote(delivery_kopecks=-1)

    def test_boolean_delivery(self) -> None:
        with self.assertRaises(TypeError):
            self.quote(delivery_kopecks=True)

    def test_zero_price_and_free_delivery(self) -> None:
        result = self.quote(items=[OrderItem(0, 1)], delivery_kopecks=0)
        self.assertEqual(result.total_kopecks, 0)

    def test_input_unchanged(self) -> None:
        original = self.items.copy()
        self.quote()
        self.assertEqual(self.items, original)


if __name__ == "__main__":
    unittest.main()
