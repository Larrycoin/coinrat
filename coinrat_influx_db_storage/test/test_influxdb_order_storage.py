from uuid import UUID

import pytest
import datetime
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import Pair
from coinrat.domain.order import Order, ORDER_TYPE_LIMIT, DIRECTION_BUY, DIRECTION_SELL, ORDER_STATUS_OPEN, \
    ORDER_STATUS_CLOSED
from coinrat_influx_db_storage.order_storage import OrderInnoDbStorage

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


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


def test_save_oder(influx_database: InfluxDBClient):
    storage = OrderInnoDbStorage(influx_database, 'test_orders')

    storage.save_order(DUMMY_ORDER)

    data = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(data) == 1
    expected = 'BUY-OPEN, ' \
               + 'Id: "16fd2706-8baf-433b-82eb-8c7fada847da", ' \
               + 'Market: "dummy_market", ' \
               + 'Created: "2017-11-26T10:11:12+00:00", ' \
               + 'Closed: "None", ' \
               + 'ID on market: "aaa-id-from-market", ' \
               + 'Pair: [USD_BTC], ' \
               + 'Type: "limit", ' \
               + 'Rate: "8000.00000000", ' \
               + 'Quantity: "1.00000000"'
    assert str(data[0]) == expected


def test_find_by(influx_database: InfluxDBClient):
    storage = OrderInnoDbStorage(influx_database, 'test_orders')

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert orders == []

    create_dummy_data(influx_database)

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


def test_delete_order(influx_database: InfluxDBClient):
    storage = OrderInnoDbStorage(influx_database, 'test_orders')
    create_dummy_data(influx_database)

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(orders) == 2

    order_id_to_delete = '16fd2706-8baf-433b-82eb-8c7fada847da'
    storage.delete(order_id_to_delete)

    orders = storage.find_by(market_name=DUMMY_MARKET, pair=BTC_USD_PAIR)
    assert len(orders) == 1
    assert orders[0].order_id != order_id_to_delete


def test_find_last_order(influx_database: InfluxDBClient):
    storage = OrderInnoDbStorage(influx_database, 'test_orders')

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


def create_dummy_data(influx_database: InfluxDBClient):
    storage = OrderInnoDbStorage(influx_database, 'test_orders')
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
