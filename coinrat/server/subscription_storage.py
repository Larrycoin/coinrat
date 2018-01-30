import logging
from typing import Dict, List, Union

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair
from coinrat.event.event_types import EVENT_LAST_CANDLE_UPDATED, EVENT_NEW_ORDER, EVENT_NEW_STRATEGY_RUN
from coinrat.domain.candle import deserialize_candle, CandleSize
from coinrat.domain.order import deserialize_order

logger = logging.getLogger(__name__)


class Subscription:
    def __init__(self, session_id: str) -> None:
        self.session_id = session_id

    def is_subscribed_for(self, event_name: Union[str, None] = None, event_data: Union[Dict, None] = None) -> bool:
        raise NotImplementedError()


class LastCandleSubscription(Subscription):
    def __init__(
        self,
        session_id: str,
        storage_name: str,
        market_name: str,
        pair: Pair,
        candle_size: CandleSize
    ) -> None:
        super().__init__(session_id)

        self.storage_name = storage_name
        self.market_name = market_name
        self.pair = pair
        self.candle_size = candle_size

    def is_subscribed_for(self, event_name: Union[str, None] = None, event_data: Union[Dict, None] = None) -> bool:
        if event_name is not None and event_name != EVENT_LAST_CANDLE_UPDATED:
            return False

        if event_data is not None:
            assert 'candle' in event_data
            assert 'storage' in event_data
            candle = deserialize_candle(event_data['candle'])

            if (
                candle.market_name != self.market_name
                or not candle.pair.is_equal(self.pair)
                or event_data['storage'] != self.storage_name
            ):
                return False

        return True

    def __repr__(self) -> str:
        return 'LastCandleSubscription({}, {}, {}, {}, {})' \
            .format(self.session_id, self.storage_name, self.market_name, self.pair, self.candle_size)


class NewOrderSubscription(Subscription):
    def __init__(
        self,
        session_id: str,
        storage_name: str,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval
    ) -> None:
        super().__init__(session_id)

        self.storage_name = storage_name
        self.market_name = market_name
        self.pair = pair
        self.interval = interval

    def is_subscribed_for(self, event_name: Union[str, None] = None, event_data: Union[Dict, None] = None) -> bool:
        if event_name is not None and event_name != EVENT_NEW_ORDER:
            return False

        if event_data is not None:
            assert 'order' in event_data
            assert 'storage' in event_data
            order = deserialize_order(event_data['order'])

            if (
                order.market_name != self.market_name
                or not order.pair.is_equal(self.pair)
                or event_data['storage'] != self.storage_name
                or not self.interval.contains(order.created_at)
            ):
                return False

        return True

    def __repr__(self) -> str:
        return 'NewOrderSubscription({}, {}, {}, {}, {})' \
            .format(self.session_id, self.storage_name, self.market_name, self.pair, self.interval)


class NewStrategyRunSubscription(Subscription):
    def __init__(self, session_id: str) -> None:
        super().__init__(session_id)

    def is_subscribed_for(self, event_name: Union[str, None] = None, event_data: Union[Dict, None] = None) -> bool:
        return event_name is not None and event_name == EVENT_NEW_STRATEGY_RUN

    def __repr__(self) -> str:
        return 'NewStrategyRunSubscription({})'.format(self.session_id)


class SubscriptionStorage:
    def __init__(self) -> None:
        self._subscriptions: List[Subscription] = []

    def subscribe(self, subscription: Subscription) -> None:
        self._subscriptions.append(subscription)
        logger.info('[EVENT] Subscribed: {}.'.format(subscription))

    def find_subscriptions_for_event(self, event_name: str, event_data: Union[Dict, None] = None) -> List[Subscription]:
        result: List[Subscription] = []
        for subscription in self._subscriptions:
            if subscription.is_subscribed_for(event_name, event_data):
                result.append(subscription)

        return result

    def unsubscribe(self, event_name: str, session_id: str) -> None:
        for subscription in self._subscriptions:
            if subscription.is_subscribed_for(event_name) and subscription.session_id == session_id:
                self._subscriptions.remove(subscription)
                logger.info('[EVENT] For session: %s, unsubscribed: %r.', session_id, subscription)
