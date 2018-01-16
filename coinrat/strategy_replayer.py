import datetime
from typing import Dict

from coinrat.domain import FrozenDateTimeFactory, Pair
from coinrat.domain.candle import CandleStorage
from coinrat.domain.order import OrderStorage
from coinrat.market_plugins import MarketPlugins
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.event.event_emitter import EventEmitter


class StrategyReplayer:
    def __init__(
        self,
        strategy_plugins: StrategyPlugins,
        market_plugins: MarketPlugins,
        event_emitter: EventEmitter
    ) -> None:
        super().__init__()
        self._strategy_plugins = strategy_plugins
        self._market_plugins = market_plugins
        self._event_emitter = event_emitter

    def replay(
        self,
        strategy_name: str,
        market_name: str,
        pair: Pair,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        start: datetime.datetime,
        end: datetime.datetime,
        configuration: Dict
    ):
        datetime_factory = FrozenDateTimeFactory(start)
        strategy = self._strategy_plugins.get_strategy(
            strategy_name,
            candle_storage,
            order_storage,
            self._event_emitter,
            datetime_factory,
            configuration
        )
        market = self._market_plugins.get_market('mock', datetime_factory, {'mocked_market_name': market_name})
        while datetime_factory.now() < end:
            strategy.tick([market], pair)
            datetime_factory.move(datetime.timedelta(seconds=30))
