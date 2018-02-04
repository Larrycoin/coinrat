import pytest
from flexmock import flexmock

from coinrat_bittrex import synchronizer_plugin, market_plugin
from coinrat_bittrex.synchronizer import BittrexSynchronizer
from coinrat_bittrex.market import BittrexMarket


def test_synchronizer_plugin():
    storage = flexmock()

    assert 'coinrat_bittrex' == synchronizer_plugin.get_name()
    assert ['bittrex'] == synchronizer_plugin.get_available_synchronizers()
    assert isinstance(synchronizer_plugin.get_synchronizer('bittrex', storage, flexmock()), BittrexSynchronizer)
    with pytest.raises(ValueError):
        synchronizer_plugin.get_synchronizer('gandalf', storage, flexmock())


def test_bittrex_market_plugin():
    assert 'coinrat_bittrex' == market_plugin.get_name()

    assert ['bittrex'] == market_plugin.get_available_markets()

    assert market_plugin.does_support_market('bittrex') is True
    assert market_plugin.does_support_market('gandalf') is False

    assert isinstance(market_plugin.get_market('bittrex', flexmock(), {}), BittrexMarket)
    with pytest.raises(ValueError):
        market_plugin.get_market('gandalf', flexmock(), {})

    assert BittrexMarket == market_plugin.get_market_class('bittrex')
    with pytest.raises(ValueError):
        market_plugin.get_market_class('gandalf')
