import pytest, datetime
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import MinuteCandle, MarketPair
from coinrat_influx_db_storage.storage import MarketInnoDbStorage


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


def test_write_candle(influx_database: InfluxDBClient):
    storage = MarketInnoDbStorage(influx_database)

    storage.write_candle(_create_dummy_candle())

    data = _get_all_from_influx_db(influx_database)
    assert 1 == len(data)
    expected_data = "{" \
                    + "'time': '2017-07-02T00:00:00Z', " \
                    + "'close': 8003, " \
                    + "'high': 8001, " \
                    + "'low': 8002, " \
                    + "'market': 'dummy_market', " \
                    + "'open': 8000, " \
                    + "'pair': 'BSD_BTC'" \
                    + "}"
    assert expected_data == str(data[0])


def test_write_candles(influx_database: InfluxDBClient):
    storage = MarketInnoDbStorage(influx_database)

    storage.write_candles([_create_dummy_candle(1), _create_dummy_candle(2)])

    data = _get_all_from_influx_db(influx_database)
    assert 2 == len(data)
    assert '2017-07-02T00:01:00Z' == data[0]['time']
    assert '2017-07-02T00:02:00Z' == data[1]['time']


def _create_dummy_candle(minute: int = 0) -> MinuteCandle:
    return MinuteCandle(
        'dummy_market',
        MarketPair('BSD', 'BTC'),
        datetime.datetime(2017, 7, 2, 0, minute, 0).replace(tzinfo=datetime.timezone.utc),
        Decimal(8000),
        Decimal(8001),
        Decimal(8002),
        Decimal(8003)
    )


def _get_all_from_influx_db(influx_database: InfluxDBClient):
    return list(influx_database.query('SELECT * FROM "candles"').get_points())
