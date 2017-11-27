import copy
from uuid import UUID

import pytest, datetime
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import Order, ORDER_TYPE_LIMIT, Pair
from coinrat_influx_db_storage.order_storage import OrderInnoDbStorage, MEASUREMENT_ORDERS_NAME
from coinrat_influx_db_storage.test.utils import get_all_from_influx_db

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')

DUMMY_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    DUMMY_MARKET,
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
    storage = OrderInnoDbStorage(influx_database)

    storage.save_order(DUMMY_ORDER)

    data = get_all_from_influx_db(influx_database, MEASUREMENT_ORDERS_NAME)
    assert len(data) == 1
    expected_data = "{" \
                    + "'time': '2017-11-26T10:11:12Z', " \
                    + "'id_on_market': 'aaa-id-from-market', " \
                    + "'is_open': True, " \
                    + "'market': 'dummy_market', " \
                    + "'order_id': '16fd2706-8baf-433b-82eb-8c7fada847da', " \
                    + "'pair': 'USD_BTC', " \
                    + "'quantity': 1, " \
                    + "'rate': 8000, " \
                    + "'type': 'limit'" \
                    + "}"
    assert str(data[0]) == expected_data


def test_get_open_orders(influx_database: InfluxDBClient):
    create_dummy_data(influx_database)
    storage = OrderInnoDbStorage(influx_database)
    orders = storage.get_open_orders(DUMMY_MARKET, BTC_USD_PAIR)
    assert len(orders) == 1
    assert orders[0].is_open is True
    assert str(orders[0].order_id) == '16fd2706-8baf-433b-82eb-8c7fada847da'


def test_find_last_order(influx_database: InfluxDBClient):
    storage = OrderInnoDbStorage(influx_database)

    order = storage.find_last_order(DUMMY_MARKET, BTC_USD_PAIR)
    assert order is None

    storage.save_order(DUMMY_ORDER)

    order = storage.find_last_order(DUMMY_MARKET, BTC_USD_PAIR)
    assert str(order.order_id) == '16fd2706-8baf-433b-82eb-8c7fada847da'

    later_order = Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
        DUMMY_MARKET,
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
    storage = OrderInnoDbStorage(influx_database)
    storage.save_order(Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
        DUMMY_MARKET,
        datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
        BTC_USD_PAIR,
        ORDER_TYPE_LIMIT,
        Decimal(1),
        Decimal(8000),
        'aaa-id-from-market',
        is_open=True
    ))
    storage.save_order(Order(
        UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
        DUMMY_MARKET,
        datetime.datetime(2017, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc),
        BTC_USD_PAIR,
        ORDER_TYPE_LIMIT,
        Decimal(2),
        Decimal(9000),
        'bbb-id-from-market',
        is_open=False
    ))
