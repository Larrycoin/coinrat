from uuid import UUID

import datetime
from decimal import Decimal

from coinrat.domain import Order, ORDER_TYPE_LIMIT, Pair, DIRECTION_BUY, DIRECTION_SELL, \
    ORDER_STATUS_OPEN, ORDER_STATUS_CLOSED
from coinrat_memory_storage.order_storage import OrderMemoryStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')

DUMMY_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    DUMMY_MARKET,
    DIRECTION_BUY,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000),
    'aaa-id-from-market'
)


def test_save_oder():
    storage = OrderMemoryStorage()
    storage.save_order(DUMMY_ORDER)

    assert storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR) == [DUMMY_ORDER]


def test_find_by():
    storage = OrderMemoryStorage()

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert orders == []

    create_dummy_data(storage)

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR, status=ORDER_STATUS_OPEN)
    assert len(orders) == 1
    assert orders[0].is_open is True
    assert str(orders[0].order_id) == '16fd2706-8baf-433b-82eb-8c7fada847da'

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR, status=ORDER_STATUS_CLOSED)
    assert len(orders) == 1
    assert orders[0].is_open is False
    assert str(orders[0].order_id) == '16fd2706-8baf-433b-82eb-8c7fada847db'

    orders = storage.find_by(market_name='yolo', pair=BTC_USD_PAIR)
    assert orders == []

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=Pair('FOO', 'BAR'))
    assert orders == []

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR, direction=DIRECTION_BUY)
    assert len(orders) == 1
    assert orders[0].is_buy() is True
    assert orders[0].is_sell() is False
    assert str(orders[0].order_id) == '16fd2706-8baf-433b-82eb-8c7fada847da'

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR, direction=DIRECTION_SELL)
    assert len(orders) == 1
    assert orders[0].is_buy() is False
    assert orders[0].is_sell() is True
    assert str(orders[0].order_id) == '16fd2706-8baf-433b-82eb-8c7fada847db'


def test_delete_order():
    storage = OrderMemoryStorage()
    create_dummy_data(storage)

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(orders) == 2

    order_id_to_delete = '16fd2706-8baf-433b-82eb-8c7fada847da'
    storage.delete(order_id_to_delete)

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(orders) == 1
    assert orders[0].order_id != order_id_to_delete


def test_find_last_order():
    storage = OrderMemoryStorage()

    order = storage.find_last_order(DUMMY_MARKET, BTC_USD_PAIR)
    assert order is None

    storage.save_order(DUMMY_ORDER)

    order = storage.find_last_order(DUMMY_MARKET, BTC_USD_PAIR)
    assert str(order.order_id) == '16fd2706-8baf-433b-82eb-8c7fada847da'

    later_order = Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
        DUMMY_MARKET,
        DIRECTION_BUY,
        datetime.datetime(2017, 11, 26, 10, 11, 13, tzinfo=datetime.timezone.utc),
        BTC_USD_PAIR,
        ORDER_TYPE_LIMIT,
        Decimal(1),
        Decimal(8000),
        'aaa-id-from-market'
    )
    storage.save_order(later_order)

    order = storage.find_last_order(DUMMY_MARKET, BTC_USD_PAIR)
    assert str(order.order_id) == '16fd2706-8baf-433b-82eb-8c7fada847db'


def create_dummy_data(storage: OrderMemoryStorage):
    storage.save_order(Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
        DUMMY_MARKET,
        DIRECTION_BUY,
        datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
        BTC_USD_PAIR,
        ORDER_TYPE_LIMIT,
        Decimal(1),
        Decimal(8000),
        'aaa-id-from-market',
        ORDER_STATUS_OPEN
    ))
    storage.save_order(Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
        DUMMY_MARKET,
        DIRECTION_SELL,
        datetime.datetime(2017, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        BTC_USD_PAIR,
        ORDER_TYPE_LIMIT,
        Decimal(2),
        Decimal(9000),
        'bbb-id-from-market',
        ORDER_STATUS_CLOSED
    ))
