from decimal import Decimal

from coinrat.domain import MarketPair, Order, ORDER_TYPE_LIMIT
from coinrat_dummy_print.market import PrintDummyMarket

BTC_USD_PAIR = MarketPair('USD', 'BTC')
DUMMY_ORDER = Order(BTC_USD_PAIR, ORDER_TYPE_LIMIT, Decimal(1), Decimal(8000))


def test_market():
    market = PrintDummyMarket()
    assert 'dummy_print' == market.get_name()
    assert Decimal(0.004) == market.get_pair_market_info(BTC_USD_PAIR).minimal_order_size
    assert '0.50000000 BTC' == str(market.get_balance('BTC'))
    assert '0.50000000 LOL' == str(market.get_balance('LOL'))
    assert Decimal(0.0025) == market.transaction_fee_coefficient
    assert 'aaaa-bbbb-cccc-dddd' == market.create_sell_order(DUMMY_ORDER)
    assert 'aaaa-bbbb-cccc-dddd' == market.create_buy_order(DUMMY_ORDER)
    assert market.cancel_order('xxx') is None
    assert 'aaaa-bbbb-cccc-dddd' == market.buy_max_available(BTC_USD_PAIR)
    assert 'aaaa-bbbb-cccc-dddd' == market.sell_max_available(BTC_USD_PAIR)
