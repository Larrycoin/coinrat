import logging

from typing import List, Dict

from coinrat.domain.candle import Candle
from coinrat.domain.order import Order
from coinrat.domain.portfolio import PortfolioSnapshot
from coinrat.domain.strategy import StrategyRun
from .event_emitter import EventEmitter

logger = logging.getLogger(__name__)


class NullEventEmitter(EventEmitter):
    def emit_new_candles(self, candle_storage: str, candles: List[Candle]) -> None:
        pass

    def emit_new_order(self, order_storage: str, order: Order, portfolio_snapshot: PortfolioSnapshot) -> None:
        pass

    def emit_event(self, event: Dict) -> None:
        pass

    def emit_new_strategy_run(self, strategy_run: StrategyRun):
        pass
