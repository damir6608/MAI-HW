def calculate_total(prices_kopecks: list[int], delivery_kopecks: int = 0) -> int:
    """Return the total in kopecks; raise TypeError or ValueError for invalid input."""
    if not isinstance(prices_kopecks, list):
        raise TypeError("prices_kopecks must be a list")
    if type(delivery_kopecks) is not int:
        raise TypeError("delivery_kopecks must be an integer")
    if delivery_kopecks < 0:
        raise ValueError("delivery_kopecks must not be negative")
    for price in prices_kopecks:
        if type(price) is not int:
            raise TypeError("each price must be an integer")
        if price < 0:
            raise ValueError("each price must not be negative")
    return sum(prices_kopecks) + delivery_kopecks
