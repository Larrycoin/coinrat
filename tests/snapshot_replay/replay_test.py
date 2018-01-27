import json
import logging
import os
import datetime
import uuid
from typing import Dict, List
from uuid import UUID

import pytest
from flexmock import flexmock
from influxdb import InfluxDBClient

from coinrat_influx_db_storage.candle_storage import CandleInnoDbStorage
from coinrat_influx_db_storage.order_storage import OrderInnoDbStorage
from coinrat.domain import FrozenDateTimeFactory, DateTimeFactory, Strategy
from coinrat.domain.pair import Pair
from coinrat.domain.market import Market
from coinrat.domain.candle import CandleExporter
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy
from coinrat_mock.market import MockMarket
from coinrat.domain.order import serialize_orders, OrderStorage
from coinrat.domain.candle import CandleStorage
from coinrat.event.event_emitter import EventEmitter

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')

UUID_MOCK_LIST = [UUID("3cf10055-68c2-43ad-b608-{0:012d}".format(number)) for number in range(1, 100)]

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
    mock_uuid()
    dataset_path = os.path.dirname(__file__) + '/' + dataset
    candle_storage = CandleInnoDbStorage(influx_database)
    import_candles_into_storage(dataset_path, candle_storage)
    order_storage = OrderInnoDbStorage(influx_database, 'test_orders')
    datetime_factory = FrozenDateTimeFactory(start)
    emitter_mock = create_emitter_mock()

    strategy = create_strategy_to_test(candle_storage, order_storage, emitter_mock, datetime_factory)
    mock_market = MockMarket(datetime_factory, {'mocked_market_name': 'bittrex'})

    run_strategy_replay(strategy, mock_market, datetime_factory, end)

    result_orders = get_created_orders_from_storage(order_storage)
    save_last_result_into_file(dataset_path, result_orders)
    assert_orders_against_expectation_file(dataset_path, result_orders)


def assert_orders_against_expectation_file(dataset_path, result_orders: List[Dict]) -> None:
    with open(dataset_path + '/orders.json') as json_file:
        expected_orders = json.load(json_file)
        assert result_orders == expected_orders


def get_created_orders_from_storage(order_storage: OrderStorage) -> List[Dict]:
    orders = order_storage.find_by(market_name='bittrex', pair=BTC_USD_PAIR)
    result_orders = serialize_orders(orders)
    return result_orders


def run_strategy_replay(
    strategy: Strategy,
    mock_market: Market,
    datetime_factory: FrozenDateTimeFactory,
    end: datetime.datetime
):
    while datetime_factory.now() < end:
        strategy.tick([mock_market], BTC_USD_PAIR)
        datetime_factory.move(datetime.timedelta(seconds=30))


def create_strategy_to_test(
    candle_storage: CandleStorage,
    order_storage: OrderStorage,
    emitter_mock: EventEmitter,
    datetime_factory: DateTimeFactory
):
    return DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        emitter_mock,
        datetime_factory,
        {
            'long_average_interval': 60 * 60,
            'short_average_interval': 15 * 60,
            'delay': 0,
        }
    )


def import_candles_into_storage(dataset_path: str, candle_storage: CandleStorage) -> None:
    exporter = CandleExporter(candle_storage)
    exporter.import_from_file(dataset_path + '/candles.json')


def mock_uuid() -> None:
    expectation = flexmock(uuid).should_receive('uuid4')
    for uuid_item in UUID_MOCK_LIST:
        expectation.and_return(uuid_item)


def create_emitter_mock() -> EventEmitter:
    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_candles')
    emitter_mock.should_receive('emit_new_order')
    return emitter_mock


def save_last_result_into_file(dataset_path: str, result_orders: List[Dict]) -> None:
    file = open(dataset_path + '/orders_last_run.json', 'w')
    file.write(json.dumps(result_orders))
    file.close()
