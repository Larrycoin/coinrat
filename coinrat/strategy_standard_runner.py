import time

from coinrat.domain import DateTimeFactory
from coinrat.domain.strategy import StrategyRunner
from coinrat.domain.strategy import StrategyRun
from coinrat.market_plugins import MarketPlugins
from coinrat.order_facade import OrderFacade
from coinrat.portfolio_snapshot_storage_plugins import PortfolioSnapshotStoragePlugins
from coinrat.strategy_plugins import StrategyPlugins
from coinrat.candle_storage_plugins import CandleStoragePlugins
from coinrat.order_storage_plugins import OrderStoragePlugins
from coinrat.event.event_emitter import EventEmitter


class StrategyStandardRunner(StrategyRunner):
    def __init__(
        self,
        candle_storage_plugins: CandleStoragePlugins,
        order_storage_plugins: OrderStoragePlugins,
        strategy_plugins: StrategyPlugins,
        market_plugins: MarketPlugins,
        portfolio_snapshot_storage_plugins: PortfolioSnapshotStoragePlugins,
        event_emitter: EventEmitter,
        datetime_factory: DateTimeFactory
    ) -> None:
        super().__init__()
        self._portfolio_snapshot_storage_plugins = portfolio_snapshot_storage_plugins
        self._order_storage_plugins = order_storage_plugins
        self._candle_storage_plugins = candle_storage_plugins
        self._strategy_plugins = strategy_plugins
        self._market_plugins = market_plugins
        self._event_emitter = event_emitter
        self._datetime_factory = datetime_factory

    def run(self, strategy_run: StrategyRun):
        order_storage = self._order_storage_plugins.get_order_storage(strategy_run.order_storage_name)
        candle_storage = self._candle_storage_plugins.get_candle_storage(strategy_run.candle_storage_name)

        # Todo: Make this configurable, see https://github.com/Achse/coinrat/issues/47
        portfolio_snapshot_storage = self._portfolio_snapshot_storage_plugins \
            .get_portfolio_snapshot_storage('influx_db')

        strategy = self._strategy_plugins.get_strategy(
            strategy_run.strategy_name,
            candle_storage,
            OrderFacade(order_storage, portfolio_snapshot_storage, self._event_emitter),
            self._datetime_factory,
            strategy_run
        )

        markets = []

        for strategy_run_market in strategy_run.markets:
            market_plugin = self._market_plugins.get_plugin(strategy_run_market.plugin_name)
            markets.append(market_plugin.get_market(
                strategy_run_market.market_name,
                self._datetime_factory,
                strategy_run_market.market_configuration
            ))

        while True:
            strategy.tick(markets)
            time.sleep(int(strategy.get_seconds_delay_between_ticks()))
