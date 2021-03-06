import json
import logging
import pika

from typing import List, Dict

from coinrat.domain.candle import Candle, serialize_candle
from coinrat.domain.order import Order
from coinrat.domain.order import serialize_order
from coinrat.domain.portfolio import PortfolioSnapshot, serialize_portfolio_snapshot
from coinrat.domain.strategy import StrategyRun
from coinrat.domain.strategy import serialize_strategy_run
from .event_emitter import EventEmitter
from .event_types import EVENT_LAST_CANDLE_UPDATED, EVENT_NEW_ORDER, EVENT_NEW_STRATEGY_RUN

logger = logging.getLogger(__name__)


class RabbitEventEmitter(EventEmitter):
    def __init__(self, rabbit_connection: pika.BlockingConnection) -> None:
        super().__init__()
        self.channel = rabbit_connection.channel()
        self.channel.queue_declare(queue='events')

    def emit_new_candles(self, candle_storage: str, candles: List[Candle]) -> None:
        for candle in candles:
            self.emit_event({
                'event': EVENT_LAST_CANDLE_UPDATED,
                'candle': serialize_candle(candle),
                'storage': candle_storage,
            })

    def emit_new_order(self, order_storage: str, order: Order, portfolio_snapshot: PortfolioSnapshot) -> None:
        data = serialize_order(order)
        data['portfolio_snapshot'] = serialize_portfolio_snapshot(portfolio_snapshot)

        self.emit_event({
            'event': EVENT_NEW_ORDER,
            'order': data,
            'storage': order_storage,
        })

    def emit_event(self, event: Dict) -> None:
        logger.debug('Emitting event: %s', event)
        self.channel.basic_publish(exchange='', routing_key='events', body=json.dumps(event))

    def emit_new_strategy_run(self, strategy_run: StrategyRun):
        self.emit_event({
            'event': EVENT_NEW_STRATEGY_RUN,
            'strategy_run': serialize_strategy_run(strategy_run),
        })
