import pytest

from coinrat_mock import market_plugin
from coinrat_mock.market import MockMarket


def test_plugin():
    assert 'coinrat_mock' == market_plugin.get_name()
    assert ['mock'] == market_plugin.get_available_markets()
    assert isinstance(market_plugin.get_market('mock'), MockMarket)
    with pytest.raises(ValueError):
        market_plugin.get_market('gandalf')
