import datetime
from typing import Dict, List
from uuid import UUID

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair


class StrategyRunMarket:
    def __init__(self, market_name: str, market_configuration: Dict) -> None:
        self.market_name = market_name
        self.market_configuration = market_configuration


class StrategyRun:
    def __init__(
        self,
        strategy_run_id: UUID,
        run_at: datetime.datetime,
        pair: Pair,
        markets: List[StrategyRunMarket],
        strategy_name: str,
        strategy_configuration: Dict,
        interval: DateTimeInterval,
        candle_storage_name: str,
        order_storage_name: str,
    ) -> None:
        assert '+00:00' in run_at.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(run_at.isoformat()))

        self.strategy_run_id = strategy_run_id
        self.run_at = run_at
        self.pair = pair
        self.markets = markets
        self.strategy_name = strategy_name
        self.strategy_configuration = strategy_configuration
        self.interval = interval
        self.candle_storage_name = candle_storage_name
        self.order_storage_name = order_storage_name
