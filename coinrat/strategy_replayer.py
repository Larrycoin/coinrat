import datetime
from typing import Dict

from coinrat.domain import FrozenDateTimeFactory, Pair
from coinrat.domain.candle import CandleStorage
from coinrat.domain.order import OrderStorage
from coinrat.market_plugins import MarketPlugins
from coinrat.strategy_plugins import StrategyPlugins


class StrategyReplayer:
    def __init__(self, strategy_plugins: StrategyPlugins, market_plugins: MarketPlugins) -> None:
        super().__init__()
        self.strategy_plugins = strategy_plugins
        self.market_plugins = market_plugins

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

        strategy = self.strategy_plugins.get_strategy(
            strategy_name,
            candle_storage,
            order_storage,
            datetime_factory,
            configuration
        )

        market = self.market_plugins.get_market(market_name, datetime_factory, {'mocked_market_name': market_name})
        print(datetime_factory.now())
        print(end)
        while datetime_factory.now() < end:
            print(1)
            strategy.tick([market], pair)
            datetime_factory.move(datetime.timedelta(seconds=10))
