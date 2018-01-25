import datetime
from typing import Dict

from coinrat.domain import FrozenDateTimeFactory, Pair
from coinrat.domain.candle import CandleStorage
from coinrat.domain.order import OrderStorage
from coinrat.market_plugins import MarketPlugins
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.event.event_emitter import EventEmitter
from coinrat.domain.configuration_structure import format_data_to_python_types


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
        market_configuration: Dict,
        strategy_configuration: Dict,
        pair: Pair,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        start: datetime.datetime,
        end: datetime.datetime
    ):
        datetime_factory = FrozenDateTimeFactory(start)

        strategy_class = self._strategy_plugins.get_strategy_class(strategy_name)
        strategy = self._strategy_plugins.get_strategy(
            strategy_name,
            candle_storage,
            order_storage,
            self._event_emitter,
            datetime_factory,
            format_data_to_python_types(strategy_configuration, strategy_class.get_configuration_structure())
        )

        market_class = self._market_plugins.get_market_class('mock')
        market = self._market_plugins.get_market(
            'mock',
            datetime_factory,
            format_data_to_python_types(market_configuration, market_class.get_configuration_structure())
        )

        while datetime_factory.now() < end:
            strategy.tick([market], pair)
            datetime_factory.move(datetime.timedelta(seconds=strategy.get_seconds_delay_between_runs()))
