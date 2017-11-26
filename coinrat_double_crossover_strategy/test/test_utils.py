import pytest
from decimal import Decimal

from coinrat_double_crossover_strategy.utils import absolute_possible_percentage_gain


@pytest.mark.parametrize(['expected', 'a', 'b'],
    [
        (Decimal(0), Decimal(1000), Decimal(1000)),
        (Decimal('0.0029910269192422731804586241'), Decimal(1000), Decimal(1003)),
        (Decimal('0.0019940179461615154536390828'), Decimal(1003), Decimal(1001)),
    ]
)
def test_absolute_possible_percentage_gain(expected: Decimal, a: Decimal, b: Decimal):
    result = absolute_possible_percentage_gain(a, b)
    assert isinstance(result, Decimal)
    assert expected == result


@pytest.mark.parametrize(['a', 'b'],
    [
        (Decimal(0), Decimal(1000)),
        (Decimal(1000), Decimal(0)),
        (Decimal(-1), Decimal(1001)),
        (Decimal(1), Decimal(-1)),
    ]
)
def test_nonsense(a: Decimal, b: Decimal):
    with pytest.raises(AssertionError):
        absolute_possible_percentage_gain(a, b)
