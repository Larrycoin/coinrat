import datetime
import os
from uuid import UUID

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair
from coinrat.domain.strategy import StrategyRun, serialize_strategy_run

current_directory = os.path.dirname(__file__)

DUMMY_DATE = datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc)


def test_serialize_strategy() -> None:
    strategy_run_market = StrategyRun(
        UUID('8b3213c8-2c07-4283-8197-a9babfcc1ec8'),
        DUMMY_DATE,
        Pair('USD', 'BTC'),
        [],
        'strategy_xyz',
        {},
        DateTimeInterval(),
        'c',
        'o'
    )
    assert serialize_strategy_run(strategy_run_market) == {
        'candle_storage_name': 'c',
        'interval': {'since': None, 'till': None},
        'markets': [],
        'order_storage_name': 'o',
        'pair': 'USD_BTC',
        'run_at': '2017-11-26T10:11:12+00:00',
        'strategy_configuration': {},
        'strategy_name': 'strategy_xyz',
        'strategy_run_id': '8b3213c8-2c07-4283-8197-a9babfcc1ec8',
    }
