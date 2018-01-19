import datetime
from decimal import Decimal
from uuid import UUID

from coinrat.domain import Pair, CurrentUtcDateTimeFactory
from coinrat.domain.order import Order, ORDER_TYPE_LIMIT, DIRECTION_BUY
from coinrat_mock.market import MockMarket

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
    market = MockMarket(
        CurrentUtcDateTimeFactory(),
        {
            'mocked_market_name': 'yolo',
            'mocked_base_currency_balance': Decimal(1001),
            'mocked_base_currency': 'WTF',
            'mocked_transaction_maker_fee': Decimal('0.001'),
            'mocked_transaction_taker_fee': Decimal('0.001'),
        }
    )
    assert 'yolo' == market.name
    assert Decimal(0.004) == market.get_pair_market_info(BTC_USD_PAIR).minimal_order_size
    assert '1001.00000000 WTF' == str(market.get_balance('WTF'))
    assert '0.00000000 LOL' == str(market.get_balance('LOL'))
    assert Decimal('0.001') == market.transaction_taker_fee
    assert Decimal('0.001') == market.transaction_maker_fee
    assert DUMMY_ORDER == market.place_order(DUMMY_ORDER)
    assert market.cancel_order('xxx') is None
