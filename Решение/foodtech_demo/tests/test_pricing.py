"""Shared acceptance tests for the same pricing contract."""

import importlib.util
import os
import unittest
from pathlib import Path

from foodtech.pricing import calculate_total

if os.environ.get("PRICING_VARIANT"):
    variant_path = Path(os.environ["PRICING_VARIANT"]).resolve()
    spec = importlib.util.spec_from_file_location("pricing_variant", variant_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the requested pricing variant")
    variant = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(variant)
    calculate_total = variant.calculate_total


class PricingTests(unittest.TestCase):
    """The business contract is identical for both generated variants."""

    def test_sum_with_delivery(self) -> None:
        self.assertEqual(calculate_total([90000, 110000], 15000), 215000)

    def test_default_delivery(self) -> None:
        self.assertEqual(calculate_total([90000]), 90000)

    def test_empty_prices(self) -> None:
        self.assertEqual(calculate_total([], 15000), 15000)

    def test_zero_price(self) -> None:
        self.assertEqual(calculate_total([0], 0), 0)

    def test_large_integer_exactness(self) -> None:
        self.assertEqual(calculate_total([10**30, 1], 2), 10**30 + 3)

    def test_input_is_unchanged(self) -> None:
        prices = [90000, 110000]
        calculate_total(prices, 15000)
        self.assertEqual(prices, [90000, 110000])

    def test_result_is_integer(self) -> None:
        self.assertIs(type(calculate_total([1, 2], 3)), int)

    def test_negative_price(self) -> None:
        with self.assertRaises(ValueError):
            calculate_total([-1])

    def test_negative_delivery(self) -> None:
        with self.assertRaises(ValueError):
            calculate_total([100], -1)

    def test_float_price(self) -> None:
        with self.assertRaises(TypeError):
            calculate_total([1.5])

    def test_boolean_price(self) -> None:
        with self.assertRaises(TypeError):
            calculate_total([True])

    def test_float_delivery(self) -> None:
        with self.assertRaises(TypeError):
            calculate_total([100], 1.5)

    def test_boolean_delivery(self) -> None:
        with self.assertRaises(TypeError):
            calculate_total([100], True)

    def test_string_price(self) -> None:
        with self.assertRaises(TypeError):
            calculate_total(["100"])

    def test_tuple_container(self) -> None:
        with self.assertRaises(TypeError):
            calculate_total((100, 200))


if __name__ == "__main__":
    unittest.main()
