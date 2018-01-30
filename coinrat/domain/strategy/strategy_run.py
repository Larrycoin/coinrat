import datetime
from typing import Dict, List, Union
from uuid import UUID

from coinrat.domain import DateTimeInterval, serialize_datetime_interval
from coinrat.domain.pair import Pair, serialize_pair


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


def serialize_strategy_run(strategy_run: StrategyRun):
    return {
        'strategy_run_id': str(strategy_run.strategy_run_id),
        'run_at': strategy_run.run_at.isoformat(),
        'pair': serialize_pair(strategy_run.pair),
        'markets': serialize_strategy_run_markets(strategy_run.markets),
        'strategy_name': strategy_run.strategy_name,
        'strategy_configuration': strategy_run.strategy_configuration,
        'interval': serialize_datetime_interval(strategy_run.interval),
        'candle_storage_name': strategy_run.candle_storage_name,
        'order_storage_name': strategy_run.order_storage_name,
    }


def serialize_strategy_runs(strategy_runs: List[StrategyRun]) -> List[Dict[str, Union[str, None]]]:
    return list(map(serialize_strategy_run, strategy_runs))


def serialize_strategy_run_market(strategy_run_market: StrategyRunMarket) -> Dict:
    return {
        'name': strategy_run_market.market_name,
        'configuration': strategy_run_market.market_configuration,
    }


def serialize_strategy_run_markets(strategy_run_markets: List[StrategyRunMarket]) -> List[Dict[str, Union[str, None]]]:
    return list(map(serialize_strategy_run_market, strategy_run_markets))
