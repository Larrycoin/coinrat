import datetime
from decimal import Decimal
from uuid import UUID

from coinrat.domain import Pair, Order, ORDER_TYPE_LIMIT, DIRECTION_BUY
from coinrat_dummy_print.market import PrintDummyMarket

BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    'dummy_market_name',
    DIRECTION_BUY,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000)
)


def test_market():
    market = PrintDummyMarket()
    assert 'dummy_print' == market.name()
    assert Decimal(0.004) == market.get_pair_market_info(BTC_USD_PAIR).minimal_order_size
    assert '0.50000000 BTC' == str(market.get_balance('BTC'))
    assert '0.50000000 LOL' == str(market.get_balance('LOL'))
    assert Decimal(0.0025) == market.transaction_fee
    assert DUMMY_ORDER == market.place_sell_order(DUMMY_ORDER)
    assert DUMMY_ORDER == market.place_buy_order(DUMMY_ORDER)
    assert market.cancel_order('xxx') is None
    buy_order = market.buy_max_available(BTC_USD_PAIR)
    assert isinstance(buy_order, Order)
    assert isinstance(buy_order.order_id, UUID)
    sell_order = market.sell_max_available(BTC_USD_PAIR)
    assert isinstance(sell_order, Order)
    assert isinstance(buy_order.order_id, UUID)
