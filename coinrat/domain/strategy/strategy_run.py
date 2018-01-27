import datetime
from typing import Dict

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair


class StrategyRun:
    def __init__(
        self,
        run_at: datetime.datetime,
        pair: Pair,
        market_name: str,
        market_configuration: Dict,
        strategy_name: str,
        strategy_configuration: Dict,
        interval: DateTimeInterval,
        candle_storage: str,
        order_storage: str,
    ) -> None:
        assert '+00:00' in run_at.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(time.isoformat()))

        self.run_at = run_at
        self.pair = pair
        self.market_name = market_name
        self.market_configuration = market_configuration
        self.strategy_name = strategy_name
        self.strategy_configuration = strategy_configuration
        self.interval = interval
        self.candle_storage = candle_storage
        self.order_storage = order_storage


