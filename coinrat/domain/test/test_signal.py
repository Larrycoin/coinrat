import pytest

from coinrat.domain import Signal, SIGNAL_BUY, SIGNAL_SELL


def test_signal():
    assert SIGNAL_BUY == str(Signal(SIGNAL_BUY))
    assert SIGNAL_SELL == str(Signal(SIGNAL_SELL))
    with pytest.raises(AssertionError):
        Signal('gandalf')
