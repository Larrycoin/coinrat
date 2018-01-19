import json
import logging
import os
import datetime
import uuid
from typing import Dict
from uuid import UUID

import pytest
from flexmock import flexmock
from influxdb import InfluxDBClient

from coinrat_influx_db_storage.candle_storage import CandleInnoDbStorage
from coinrat_influx_db_storage.order_storage import OrderInnoDbStorage
from coinrat.domain import Pair, FrozenDateTimeFactory
from coinrat.domain.candle import CandleExporter
from coinrat.domain.order import Order
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy
from coinrat_mock.market import MockMarket

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')

uuid_mock_list = [UUID("3cf10055-68c2-43ad-b608-{0:012d}".format(number)) for number in range(1, 100)]

logging.disable(logging.DEBUG)


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


@pytest.mark.parametrize(
    ['dataset', 'start', 'end'],
    [
        (
            'double_crossover_strategy_1',
            datetime.datetime(2017, 12, 2, 14, 0, 0, tzinfo=datetime.timezone.utc),
            datetime.datetime(2017, 12, 2, 22, 0, 0, tzinfo=datetime.timezone.utc)
        ),
    ]
)
def test_candle_ticks_are_stored(
    influx_database: InfluxDBClient,
    dataset: str,
    start: datetime.datetime,
    end: datetime.datetime
):
    expectation = flexmock(uuid).should_receive('uuid4')
    for uuid_item in uuid_mock_list:
        expectation.and_return(uuid_item)

    dataset_path = os.path.dirname(__file__) + '/' + dataset

    candle_storage = CandleInnoDbStorage(influx_database)
    order_storage = OrderInnoDbStorage(influx_database)

    exporter = CandleExporter(candle_storage)
    exporter.import_from_file(dataset_path + '/candles.json')

    datetime_factory = FrozenDateTimeFactory(start)

    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_candles')
    emitter_mock.should_receive('emit_new_order')

    strategy_configuration = {
        'long_average_interval': 60 * 60,
        'short_average_interval': 15 * 60,
        'delay': 0,
    }

    strategy = DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        emitter_mock,
        datetime_factory,
        strategy_configuration
    )
    market_configuration = {'mocked_market_name': 'bittrex'}
    mock_market = MockMarket(datetime_factory, market_configuration)

    while datetime_factory.now() < end:
        strategy.tick([mock_market], BTC_USD_PAIR)
        datetime_factory.move(datetime.timedelta(seconds=30))

    orders = order_storage.find_by(market_name='bittrex', pair=BTC_USD_PAIR)
    result_orders = list(map(_data_to_order, orders))

    file = open(dataset_path + '/orders_last_run.json', 'w')
    file.write(json.dumps(result_orders))
    file.close()

    with open(dataset_path + '/orders.json') as json_file:
        expected_orders = json.load(json_file)
        assert result_orders == expected_orders


def _data_to_order(order: Order) -> Dict:
    return {
        "time": order.created_at.isoformat(),
        "direction": order._direction,
        "market": order.market_name,
        "order_id": str(order.order_id),
        "pair": str(order.pair),
        "quantity": str(order.quantity),
        "rate": str(order.rate),
        "status": order._status,
        "type": order.type
    }
