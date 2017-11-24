import pytest

from coinrat_dummy_print import market_plugin
from coinrat_dummy_print.market import PrintDummyMarket


def test_plugin():
    assert 'coinrat_dummy_print' == market_plugin.get_name()
    assert ['dummy_print'] == market_plugin.get_available_markets()
    assert isinstance(market_plugin.get_market('dummy_print'), PrintDummyMarket)
    with pytest.raises(ValueError):
        market_plugin.get_market('gandalf')
