from decimal import Decimal

from coinrat.domain import Market, PairMarketInfo, MarketPair


def test_market():
    candle = Market()
    candle.get_name = lambda: 'dummy_name'

    assert 'dummy_name' == str(candle)


def test_pair_market_info():
    info = PairMarketInfo(MarketPair('USD', 'BTC'), Decimal(0.0003))

    assert 'Pair: [USD-BTC], minimal order size: 0.00030000000' == str(info)
