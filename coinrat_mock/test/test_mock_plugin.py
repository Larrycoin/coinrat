import pytest
from flexmock import flexmock

from coinrat_mock import market_plugin
from coinrat_mock.market import MockMarket


def test_mock_market_plugin():
    assert 'coinrat_mock' == market_plugin.get_name()
    assert [] == market_plugin.get_available_markets()

    assert market_plugin.does_support_market('gandalf') is False
    with pytest.raises(ValueError):
        market_plugin.get_market('gandalf', flexmock(), {})
    with pytest.raises(ValueError):
        market_plugin.get_market_class('gandalf')

    market_plugin.set_available_markets(['gandalf'])

    assert market_plugin.does_support_market('gandalf') is True
    assert isinstance(market_plugin.get_market('gandalf', flexmock(), {}), MockMarket)
    assert MockMarket == market_plugin.get_market_class('gandalf')
