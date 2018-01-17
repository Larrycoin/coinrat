import json
import os
import datetime
import uuid
from typing import Dict
from uuid import UUID

import pytest
from flexmock import flexmock

from coinrat.domain import Pair, FrozenDateTimeFactory
from coinrat.domain.candle import CandleExporter
from coinrat.domain.order import Order
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy
from coinrat_mock.market import MockMarket
from coinrat_memory_storage.candle_storage import CandleMemoryStorage
from coinrat_memory_storage.order_storage import OrderMemoryStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')

uuid_mock_list = [UUID("3cf10055-68c2-43ad-b608-{0:012d}".format(number)) for number in range(1, 100)]


@pytest.mark.parametrize(['dataset', 'start', 'end'],
    [
        (
            'double_crossover_strategy_1',
            datetime.datetime(2017, 12, 2, 14, 0, 0, tzinfo=datetime.timezone.utc),
            datetime.datetime(2017, 12, 2, 22, 0, 0, tzinfo=datetime.timezone.utc)
        ),
    ]
)
def test_candle_ticks_are_stored(
    dataset: str,
    start: datetime.datetime,
    end: datetime.datetime
):
    expectation = flexmock(uuid).should_receive('uuid4')
    for uuid_item in uuid_mock_list:
        expectation.and_return(uuid_item)

    dataset_path = os.path.dirname(__file__) + '/' + dataset

    candle_storage = CandleMemoryStorage()
    order_storage = OrderMemoryStorage()

    exporter = CandleExporter(candle_storage)
    exporter.import_from_file(dataset_path + '/candles.json')

    datetime_factory = FrozenDateTimeFactory(start)

    # todo: use StrategyReplayer

    strategy = DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        datetime_factory,
        60 * 60,
        15 * 60,
        0
    )

    market = MockMarket(datetime_factory, name='bittrex')

    while datetime_factory.now() < end:
        strategy.tick([market], BTC_USD_PAIR)
        datetime_factory.move(datetime.timedelta(seconds=10))

    orders = order_storage.find_by(market_name='bittrex', pair=BTC_USD_PAIR)
    result_orders = list(map(_data_to_order, orders))

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
