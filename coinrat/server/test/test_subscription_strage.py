import datetime
import uuid

from decimal import Decimal

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair
from coinrat.domain.candle import Candle, CandleSize, CANDLE_SIZE_UNIT_MINUTE, serialize_candle
from coinrat.domain.order import serialize_order, Order, DIRECTION_SELL, ORDER_TYPE_LIMIT
from coinrat.server.subscription_storage import SubscriptionStorage, NewOrderSubscription, LastCandleSubscription
from coinrat.event.event_types import EVENT_NEW_ORDER, EVENT_LAST_CANDLE_UPDATED


def test_subscription_can_be_found():
    storage = SubscriptionStorage()
    last_candle_subscription = LastCandleSubscription(
        '1',
        'foo_storage',
        'bar_market',
        Pair('USD', 'BTC'),
        CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)
    )
    storage.subscribe(last_candle_subscription)
    subscription_interval = DateTimeInterval(
        datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        datetime.datetime(2018, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
    )
    date_in_interval = datetime.datetime(2018, 1, 1, 12, 0, 0, tzinfo=datetime.timezone.utc)
    date_outside_interval = datetime.datetime(2018, 1, 3, 0, 0, tzinfo=datetime.timezone.utc)
    new_order_subscription = NewOrderSubscription(
        '1',
        'foo_storage',
        'bar_market',
        Pair('USD', 'BTC'),
        subscription_interval
    )
    storage.subscribe(new_order_subscription)

    assert storage.find_subscriptions_for_event('unknown_event_name') == []

    candle_suitable_for_subscription = Candle(
        'bar_market',
        Pair('USD', 'BTC'),
        date_in_interval,
        Decimal('11000'),
        Decimal('11000'),
        Decimal('11000'),
        Decimal('11000')
    )

    assert storage.find_subscriptions_for_event(EVENT_LAST_CANDLE_UPDATED)[0] == last_candle_subscription
    assert storage.find_subscriptions_for_event(
        EVENT_LAST_CANDLE_UPDATED,
        {'storage': 'foo_storage', 'candle': serialize_candle(candle_suitable_for_subscription)}
    )[0] == last_candle_subscription
    assert storage.find_subscriptions_for_event(
        EVENT_LAST_CANDLE_UPDATED,
        {'storage': 'gandalf', 'candle': serialize_candle(candle_suitable_for_subscription)}
    ) == []
    assert storage.find_subscriptions_for_event(
        EVENT_LAST_CANDLE_UPDATED,
        {
            'storage': 'foo_storage',
            'candle': serialize_candle(
                Candle(
                    'bar_market',
                    Pair('OMG', 'WTF'),
                    date_in_interval,
                    Decimal('11000'),
                    Decimal('11000'),
                    Decimal('11000'),
                    Decimal('11000')
                )
            )
        }
    ) == []
    assert storage.find_subscriptions_for_event(
        EVENT_LAST_CANDLE_UPDATED,
        {
            'storage': 'foo_storage',
            'candle': serialize_candle(
                Candle(
                    'wtf_market',
                    Pair('USD', 'BTC'),
                    date_in_interval,
                    Decimal('11000'),
                    Decimal('11000'),
                    Decimal('11000'),
                    Decimal('11000')
                )
            )
        }
    ) == []

    order_suitable_for_subscription = _crate_serialized_order(Pair('USD', 'BTC'), 'bar_market', date_in_interval)

    assert storage.find_subscriptions_for_event(EVENT_NEW_ORDER)[0] == new_order_subscription
    assert storage.find_subscriptions_for_event(
        EVENT_NEW_ORDER,
        {'storage': 'foo_storage', 'order': order_suitable_for_subscription}
    )[0] == new_order_subscription
    assert storage.find_subscriptions_for_event(
        EVENT_NEW_ORDER,
        {'storage': 'gandalf', 'order': order_suitable_for_subscription}
    ) == []
    assert storage.find_subscriptions_for_event(
        EVENT_NEW_ORDER,
        {
            'storage': 'foo_storage',
            'order': _crate_serialized_order(Pair('USD', 'BTC'), 'bar_market', date_outside_interval)
        }
    ) == []
    assert storage.find_subscriptions_for_event(
        EVENT_NEW_ORDER,
        {
            'storage': 'foo_storage',
            'order': _crate_serialized_order(Pair('OMG', 'WTF'), 'bar_market', date_in_interval)
        }
    ) == []
    assert storage.find_subscriptions_for_event(
        EVENT_NEW_ORDER,
        {
            'storage': 'foo_storage',
            'order': _crate_serialized_order(Pair('USD', 'BTC'), 'wtf_market', date_in_interval)
        }
    ) == []

    storage.unsubscribe(EVENT_NEW_ORDER, '2')
    assert storage.find_subscriptions_for_event(EVENT_NEW_ORDER)[0] == new_order_subscription
    storage.unsubscribe(EVENT_NEW_ORDER, '1')
    assert storage.find_subscriptions_for_event(EVENT_NEW_ORDER) == []

    storage.unsubscribe(EVENT_LAST_CANDLE_UPDATED, '2')
    assert storage.find_subscriptions_for_event(EVENT_LAST_CANDLE_UPDATED)[0] == last_candle_subscription
    storage.unsubscribe(EVENT_LAST_CANDLE_UPDATED, '1')
    assert storage.find_subscriptions_for_event(EVENT_LAST_CANDLE_UPDATED) == []


def _crate_serialized_order(pair: Pair, market_name: str, created_at: datetime.datetime):
    return serialize_order(
        Order(
            uuid.uuid4(),
            uuid.UUID('99fd2706-8baf-433b-82eb-8c7fada847da'),
            market_name,
            DIRECTION_SELL,
            created_at,
            pair,
            ORDER_TYPE_LIMIT,
            Decimal('1'),
            Decimal('11000')
        ))
