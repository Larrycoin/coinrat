import pytest
from flexmock import flexmock

from coinrat_mock import market_plugin
from coinrat_mock.market import MockMarket


def test_plugin():
    assert 'coinrat_mock' == market_plugin.get_name()

    assert ['mock'] == market_plugin.get_available_markets()

    assert isinstance(market_plugin.get_market('mock', flexmock(), {}), MockMarket)
    with pytest.raises(ValueError):
        market_plugin.get_market('gandalf', flexmock(), {})

    assert MockMarket == market_plugin.get_market_class('mock')
    with pytest.raises(ValueError):
        market_plugin.get_market_class('gandalf')
