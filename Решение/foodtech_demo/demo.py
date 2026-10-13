"""Run a deterministic order example without personal data or external services."""

import json
from dataclasses import asdict
from datetime import date

from foodtech.orders import OrderItem, quote_order


def main() -> None:
    """Print the validated sample order as JSON."""
    quote = quote_order(
        [OrderItem(90000, 2), OrderItem(110000, 1)],
        days=7,
        first_delivery=date(2026, 10, 14),
        today=date(2026, 10, 12),
        delivery_kopecks=15000,
    )
    print(json.dumps(asdict(quote), ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()
