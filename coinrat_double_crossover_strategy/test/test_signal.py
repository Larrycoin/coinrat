import pytest
from decimal import Decimal

from coinrat_double_crossover_strategy.signal import Signal, SIGNAL_BUY, SIGNAL_SELL


def test_signal():
    assert SIGNAL_BUY == str(Signal(SIGNAL_BUY, Decimal(8000)))
    assert SIGNAL_SELL == str(Signal(SIGNAL_SELL, Decimal(8000)))
    with pytest.raises(AssertionError):
        Signal('gandalf', Decimal(8000))
