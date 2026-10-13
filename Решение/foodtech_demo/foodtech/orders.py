"""Validate and calculate a fixed ready meal order."""

from dataclasses import dataclass
from datetime import date, timedelta

from foodtech.pricing import calculate_total

MIN_DELIVERY_LEAD_DAYS = 2
ALLOWED_DURATIONS = (1, 7)


@dataclass(frozen=True)
class OrderItem:
    """Daily price in kopecks and the number of identical meal sets."""

    unit_price_kopecks: int
    quantity: int


@dataclass(frozen=True)
class OrderQuote:
    """Validated order totals in kopecks."""

    subtotal_kopecks: int
    delivery_kopecks: int
    total_kopecks: int
    first_delivery: date
    days: int


def quote_order(
    items: list[OrderItem],
    days: int,
    first_delivery: date,
    today: date,
    delivery_kopecks: int = 0,
) -> OrderQuote:
    """Quote 1 or 7 days; raise TypeError/ValueError for invalid input or early delivery."""
    if not isinstance(items, list):
        raise TypeError("items must be a list")
    if not items:
        raise ValueError("order must contain at least one item")
    if type(days) is not int:
        raise TypeError("days must be an integer")
    if days not in ALLOWED_DURATIONS:
        raise ValueError("days must be 1 or 7")
    if type(today) is not date or type(first_delivery) is not date:
        raise TypeError("today and first_delivery must be dates without time")
    if (first_delivery - today) < timedelta(days=MIN_DELIVERY_LEAD_DAYS):
        raise ValueError("first delivery requires at least 2 calendar days")

    line_totals: list[int] = []
    for item in items:
        if not isinstance(item, OrderItem):
            raise TypeError("each item must be an OrderItem")
        if type(item.unit_price_kopecks) is not int or type(item.quantity) is not int:
            raise TypeError("price and quantity must be integers")
        if item.unit_price_kopecks < 0:
            raise ValueError("price must not be negative")
        if item.quantity <= 0:
            raise ValueError("quantity must be positive")
        line_totals.append(item.unit_price_kopecks * item.quantity * days)

    subtotal = calculate_total(line_totals)
    total = calculate_total([subtotal], delivery_kopecks)
    return OrderQuote(subtotal, delivery_kopecks, total, first_delivery, days)
