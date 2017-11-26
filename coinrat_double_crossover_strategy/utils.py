from decimal import Decimal


def absolute_possible_percentage_gain(a: Decimal, b: Decimal) -> Decimal:
    assert a > 0
    assert b > 0
    return Decimal(1) - min(a, b) / max(a, b)
