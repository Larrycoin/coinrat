from typing import Union, Tuple, List, Dict
from decimal import Decimal

import math

from coinrat.domain import Strategy, Pair, Market, MarketOrderException, StrategyConfigurationException, \
    DateTimeFactory, DateTimeInterval
from coinrat.domain.candle import CandleStorage, CANDLE_STORAGE_FIELD_CLOSE
from coinrat.domain.order import Order, OrderStorage, DIRECTION_SELL, DIRECTION_BUY, ORDER_STATUS_OPEN, \
    NotEnoughBalanceToPerformOrderException
from coinrat.event.event_emitter import EventEmitter

STRATEGY_NAME = 'heikin_ashi'


class DoubleCrossoverStrategy(Strategy):
    """
    @link http://www.humbletraders.com/heikin-ashi-trading-strategy/
    """

    def __init__(
        self,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        event_emitter: EventEmitter,
        datetime_factory: DateTimeFactory,
        configuration
    ) -> None:
        # configuration = self.fill_missing_values_with_default(configuration)

        delay: int = configuration['delay']
        number_of_runs: Union[int, None] = configuration['number_of_runs']

        self._candle_storage = candle_storage
        self._order_storage = order_storage
        self._event_emitter = event_emitter
        self._datetime_factory = datetime_factory
        self._delay = delay
        self._number_of_runs = number_of_runs

    def run(self, markets: List[Market], pair: Pair) -> None:
        while self._should_run():
            self.tick(markets, pair)

    def tick(self, markets: List[Market], pair: Pair) -> None:
        pass

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {}

    def _should_run(self) -> bool:
        return self._number_of_runs is None or self._number_of_runs > 0
