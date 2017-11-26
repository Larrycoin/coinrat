from typing import Tuple
from uuid import UUID

import pytest, datetime
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import Order, ORDER_TYPE_LIMIT, Pair
from coinrat_influx_db_storage.order_storage import OrderInnoDbStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')

DUMMY_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    'dummy_market_name',
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000)
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

    data = _get_all_from_influx_db(influx_database)
    assert 1 == len(data)
    expected_data = "{" \
                    + "'time': '2017-11-26T10:11:12Z', " \
                    + "'market': 'dummy_market_name', " \
                    + "'order_id': '16fd2706-8baf-433b-82eb-8c7fada847da', " \
                    + "'pair': 'USD_BTC', " \
                    + "'quantity': 1, " \
                    + "'rate': 8000, " \
                    + "'type': 'limit'" \
                    + "}"
    assert expected_data == str(data[0])


def _get_all_from_influx_db(influx_database: InfluxDBClient):
    return list(influx_database.query('SELECT * FROM "orders"').get_points())
