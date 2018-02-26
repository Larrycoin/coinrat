import logging
from typing import List, Union

import datetime

from coinrat.domain import DateTimeInterval
from coinrat.domain.market.market import Market, MarketException
from coinrat.domain.order import Order, OrderStorage
from coinrat.domain.pair import Pair
from coinrat.domain.portfolio import PortfolioSnapshot, PortfolioSnapshotStorage
from coinrat.event.event_emitter import EventEmitter

logger = logging.getLogger(__name__)


class OrderFacade:
    def __init__(
        self,
        order_storage: OrderStorage,
        portfolio_snapshot_storage: PortfolioSnapshotStorage,
        event_emitter: EventEmitter
    ) -> None:
        self._order_storage = order_storage
        self._portfolio_snapshot_storage = portfolio_snapshot_storage
        self._event_emitter = event_emitter

    def create(self, market: Market, order: Order):
        portfolio_snapshot = PortfolioSnapshot(
            order.created_at,
            market.name,
            order.order_id,
            order.strategy_run_id,
            market.get_balances()
        )
        market.place_order(order)
        self._event_emitter.emit_new_order(self._order_storage.name, order, portfolio_snapshot)
        self._order_storage.save_order(order)
        self._portfolio_snapshot_storage.save(portfolio_snapshot)

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        status: Union[str, None] = None,
        direction: Union[str, None] = None,
        interval: DateTimeInterval = DateTimeInterval(None, None),
        strategy_run_id: Union[str, None] = None
    ) -> List[Order]:
        return self._order_storage.find_by(market_name, pair, status, direction, interval, strategy_run_id)

    def find_last_order(self, market_name: str, pair: Pair) -> Union[Order, None]:
        return self._order_storage.find_last_order(market_name, pair)

    def delete(self, order_id) -> None:
        self._order_storage.delete(order_id)

    def close(self, order: Order, closed_at: datetime.datetime) -> None:
        order.close(closed_at)
        self._order_storage.delete(order.order_id)
        self._order_storage.save_order(order)
        logger.info('Order "{}" has been successfully CLOSED.'.format(order.order_id))

    def cancel(self, market: Market, order: Order, canceled_at: datetime.datetime):
        try:
            market.cancel_order(order.id_on_market)
        except MarketException as e:
            logger.error('Order "{}" cancelling failed: Error: "{}"!'.format(order.order_id, e))
            return

        order.cancel(canceled_at)
        self._order_storage.save_order(order)
        logger.info('Order "{}" has been CANCELED!'.format(order.order_id))
