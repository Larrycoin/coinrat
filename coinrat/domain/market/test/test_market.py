from decimal import Decimal
from flexmock import flexmock

from coinrat.domain.pair import Pair
from coinrat.domain.market import Market, PairMarketInfo


def test_market():
    market = Market()
    flexmock(market, name='dummy_name')

    assert 'dummy_name' == str(market)


def test_pair_market_info():
    info = PairMarketInfo(Pair('USD', 'BTC'), Decimal('0.0003'))

    assert 'Pair: [USD_BTC], minimal order size: 0.0003' == str(info)
