import datetime

from coinrat.domain import FrozenDateTimeFactory
from coinrat.domain.strategy import StrategyRunner
from coinrat.domain.strategy import StrategyRun
from coinrat.market_plugins import MarketPlugins
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.order_storage_plugins import OrderStoragePlugins
from coinrat.event.event_emitter import EventEmitter
from coinrat.domain.configuration_structure import format_data_to_python_types


class StrategyReplayer(StrategyRunner):
    def __init__(
        self,
        candle_storage_plugins: CandleStoragePlugins,
        orders_storage_plugins: OrderStoragePlugins,
        strategy_plugins: StrategyPlugins,
        market_plugins: MarketPlugins,
        event_emitter: EventEmitter
    ) -> None:
        super().__init__()
        self._order_storage_plugins = orders_storage_plugins
        self._candle_storage_plugins = candle_storage_plugins
        self._strategy_plugins = strategy_plugins
        self._market_plugins = market_plugins
        self._event_emitter = event_emitter

    def run(self, strategy_run: StrategyRun):
        assert strategy_run.interval.is_closed(), 'Strategy replayer cannot run simulation for non-closed interval'

        order_storage = self._order_storage_plugins.get_order_storage(strategy_run.order_storage_name)
        candle_storage = self._candle_storage_plugins.get_candle_storage(strategy_run.candle_storage_name)

        datetime_factory = FrozenDateTimeFactory(strategy_run.interval.since)

        strategy = self._strategy_plugins.get_strategy(
            strategy_run.strategy_name,
            candle_storage,
            order_storage,
            self._event_emitter,
            datetime_factory,
            strategy_run
        )

        strategy_run_market = strategy_run.markets[0]  # Todo: solve multi-market strategies
        assert strategy_run_market.plugin_name == 'coinrat_mock', \
            'Market plugin must be "coinrat_mock" for simulations, "{}" given.'.format(strategy_run_market.plugin_name)

        market_plugin = self._market_plugins.get_plugin(strategy_run_market.plugin_name)
        market_class = market_plugin.get_market_class(strategy_run_market.market_name)

        market = market_plugin.get_market(
            strategy_run_market.market_name,
            datetime_factory,
            format_data_to_python_types(
                strategy_run_market.market_configuration,
                market_class.get_configuration_structure()
            )
        )

        while datetime_factory.now() < strategy_run.interval.till:
            current_candle = candle_storage.get_last_minute_candle(
                market.name,
                strategy_run.pair,
                datetime_factory.now()
            )
            market.mock_current_price(strategy_run.pair, current_candle.average_price)
            strategy.tick([market])
            datetime_factory.move(datetime.timedelta(seconds=strategy.get_seconds_delay_between_ticks()))
