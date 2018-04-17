from typing import Dict

from coinrat.domain import deserialize_datetime_interval
from coinrat.domain.candle import deserialize_candle_size
from coinrat.domain.pair import deserialize_pair
from coinrat.event.event_types import EVENT_NEW_ORDER, EVENT_LAST_CANDLE_UPDATED, EVENT_NEW_STRATEGY_RUN
from coinrat.server.subscription_storage import LastCandleSubscription, NewStrategyRunSubscription, NewOrderSubscription


def create_subscription(session_id: str, data: Dict):
    if data['event'] == EVENT_LAST_CANDLE_UPDATED:
        return LastCandleSubscription(
            session_id,
            data['storage'],
            data['market'],
            deserialize_pair(data['pair']),
            deserialize_candle_size(data['candle_size'])
        )
    elif data['event'] == EVENT_NEW_ORDER:
        return NewOrderSubscription(
            session_id,
            data['storage'],
            data['market'],
            deserialize_pair(data['pair']),
            deserialize_datetime_interval(data['interval'])
        )
    elif data['event'] == EVENT_NEW_STRATEGY_RUN:
        return NewStrategyRunSubscription(session_id)
    else:
        raise ValueError('Event "{}" not supported'.format(data['event']))
