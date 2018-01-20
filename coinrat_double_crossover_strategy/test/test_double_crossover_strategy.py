import datetime
import logging
from typing import List, Union, Tuple
from uuid import UUID

import pytest
from decimal import Decimal
from flexmock import flexmock, Mock

from coinrat.domain import Pair, Market, StrategyConfigurationException, CurrentUtcDateTimeFactory
from coinrat.domain.order import ORDER_TYPE_LIMIT, Order, OrderMarketInfo, DIRECTION_BUY, DIRECTION_SELL, \
    NotEnoughBalanceToPerformOrderException, ORDER_STATUS_CLOSED, ORDER_STATUS_OPEN, OrderStorage
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy
from coinrat.event.event_emitter import EventEmitter

DUMMY_MARKET_NAME = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_CLOSED_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    DUMMY_MARKET_NAME,
    DIRECTION_BUY,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000),
    'aaa-id-from-market',
    ORDER_STATUS_CLOSED,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc)
)
DUMMY_OPEN_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
    DUMMY_MARKET_NAME,
    DIRECTION_BUY,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000),
    'aaa-id-from-market'
)


@pytest.mark.parametrize(
    ['error', 'markets'],
    [
        (True, []),
        (False, [flexmock()]),
        (True, [flexmock(), flexmock()]),
    ]
)
def test_number_of_markets_validation(error: bool, markets: List[Union[Market, Mock]]):
    candle_storage = flexmock()
    candle_storage.should_receive('mean').and_return(0).mock()
    candle_storage.should_receive('get_last_minute_candle').and_return(flexmock(average_price=Decimal(8000)))

    if len(markets) == 1:  # Flexmock is not working properly with @pytest.mark.parametrize (MethodSignatureError)
        markets = [markets[0].should_receive('name').and_return(DUMMY_MARKET_NAME).mock()]

    order_storage = create_order_storage_mock()
    order_storage.should_receive('find_by').and_return([])
    order_storage.should_receive('find_last_order').and_return(None)

    strategy = DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        create_event_emitter_mock(),
        CurrentUtcDateTimeFactory(),
        {
            'long_average_interval': 60 * 60,
            'short_average_interval': 15 * 60,
            'delay': 0,
            'number_of_runs': 1,
        }
    )
    if error:
        with pytest.raises(StrategyConfigurationException):
            strategy.run(markets, BTC_USD_PAIR)
    else:
        strategy.run(markets, BTC_USD_PAIR)


@pytest.mark.parametrize(
    [
        'expected_buy',
        'expected_sell',
        'canceled_orders_count',
        'mean_evolution',
        'previous_order_rate',
        'current_candle_average_price',
    ],
    [
        (0, 0, 0, [(8000, 7800), (8000, 7900)], None, 7950),  # Short rise, but is still beneath long average
        (0, 0, 0, [(8000, 7800), (8000, 7800)], None, 7750),  # Short lowers beneath long average
        (0, 0, 0, [(8000, 8200), (8000, 8100)], None, 8050),  # Short lowers, but still uppers long average
        (0, 0, 0, [(8000, 8100), (8000, 8200)], None, 8250),  # Short rise, uppers long

        (1, 0, 1, [(8000, 7900), (8000, 8100)], None, 8150),  # Short rise, crossing long average
        (0, 1, 1, [(8000, 8100), (8000, 7900)], None, 7850),  # Short lowers, crossing long average

        (0, 0, 1, [(8000, 7999), (8000, 8001)], 7998, 8002),  # Short rise, crossing long average, but NOT WORTH IT
        (0, 0, 1, [(8000, 8001), (8000, 7999)], 8002, 7998),  # Short lowers, crossing long average, but NOT WORTH IT

        (1, 0, 1, [(8000, 7999), (8000, 8001)], 7998, 8050),  # Short rise, crossing long average, and WORTH IT
        (0, 1, 1, [(8000, 8001), (8000, 7999)], 8002, 7950),  # Short lowers, crossing long average, and  WORTH IT

        (0, 0, 0, [(8000, 8000), (8000, 8000)], None, 8000),  # Limit situations
        (0, 0, 0, [(8000, 8000), (8000, 8001)], None, 8001),  #
        (0, 0, 0, [(8000, 8001), (8000, 8000)], None, 8000),  #

        (0, 0, 0, [(8000, 7999), (8000, 8000), (8000, 7999)], None, 7999),  # just touching the crossing
        (0, 0, 0, [(8000, 8001), (8000, 8000), (8000, 8001)], None, 8001),  # just touching the crossing

        (1, 0, 1, [(8000, 7999), (8000, 8000), (8000, 8001)], None, 8001),  # very smooth crossing in more steps
        (0, 1, 1, [(8000, 8001), (8000, 8000), (8000, 7999)], None, 7999),  # very smooth crossing in more steps
    ]
)
def test_sending_signal(
    expected_buy: int,
    expected_sell: int,
    canceled_orders_count: int,
    mean_evolution: List[Tuple[int, int]],
    previous_order_rate: Union[int, None],
    current_candle_average_price: int,
):
    candle_storage = flexmock()
    expectation = candle_storage.should_receive('mean')
    for mean in mean_evolution:
        expectation.and_return(mean[0]).and_return(mean[1])
    candle_storage.should_receive('get_last_minute_candle').and_return(
        flexmock(average_price=Decimal(current_candle_average_price))
    )
    market = create_market_mock()

    class OrderDirectionMatcher(object):
        def __init__(self, direction): self._direction = direction

        def __eq__(self, order: Order): return self._direction == order._direction

    market.should_receive('place_order') \
        .with_args(OrderDirectionMatcher(DIRECTION_BUY)) \
        .and_return(DUMMY_CLOSED_ORDER) \
        .times(expected_buy)

    market.should_receive('place_order') \
        .with_args(OrderDirectionMatcher(DIRECTION_SELL)) \
        .and_return(DUMMY_CLOSED_ORDER) \
        .times(expected_sell)

    market.should_receive('cancel_order').with_args(DUMMY_OPEN_ORDER.id_on_market).times(canceled_orders_count)

    order_storage = flexmock(name='yolo_order_storage')
    order_storage.should_receive('find_by').with_args(
        market_name=DUMMY_MARKET_NAME,
        pair=BTC_USD_PAIR,
        status=ORDER_STATUS_OPEN
    ).and_return([])
    order_storage.should_receive('find_by').with_args(
        market_name=DUMMY_MARKET_NAME,
        pair=BTC_USD_PAIR,
        status=ORDER_STATUS_OPEN,
        direction=DIRECTION_BUY
    ).and_return([DUMMY_OPEN_ORDER])
    order_storage.should_receive('find_by').with_args(
        market_name=DUMMY_MARKET_NAME,
        pair=BTC_USD_PAIR,
        status=ORDER_STATUS_OPEN,
        direction=DIRECTION_SELL
    ).and_return([DUMMY_OPEN_ORDER])
    order_storage.should_receive('save_order').times(expected_buy + expected_sell + canceled_orders_count)

    previous_order = None
    if previous_order_rate is not None:
        previous_order = flexmock(rate=Decimal(previous_order_rate))
    order_storage.should_receive('find_last_order').and_return(previous_order)

    strategy = DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        create_event_emitter_mock(),
        CurrentUtcDateTimeFactory(),
        {
            'long_average_interval': 60 * 60,
            'short_average_interval': 15 * 60,
            'delay': 0,
            'number_of_runs': len(mean_evolution),
        }

    )
    strategy.run([market], BTC_USD_PAIR)


def test_not_enough_balance_logs_warning():
    candle_storage = flexmock()
    candle_storage.should_receive('mean').and_return(8000).and_return(7900).and_return(8000).and_return(8100)
    candle_storage.should_receive('get_last_minute_candle').and_return(flexmock(average_price=Decimal(Decimal(8000))))

    market = create_market_mock()
    market.should_receive('place_order').and_raise(NotEnoughBalanceToPerformOrderException)

    order_storage = create_order_storage_mock()
    order_storage.should_receive('find_by').and_return([])
    order_storage.should_receive('find_last_order').and_return(None)

    strategy = DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        create_event_emitter_mock(),
        CurrentUtcDateTimeFactory(),
        {
            'long_average_interval': 60 * 60,
            'short_average_interval': 15 * 60,
            'delay': 0,
            'number_of_runs': 2,
        }
    )
    flexmock(logging).should_receive('warning').once()
    strategy.run([market], BTC_USD_PAIR)


CLOSED_ORDER_INFO = OrderMarketInfo(
    order=DUMMY_OPEN_ORDER,
    is_open=False,
    closed_at=datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    quantity_remaining=Decimal(0)
)

STILL_OPEN_ORDER_INFO = OrderMarketInfo(
    order=DUMMY_OPEN_ORDER,
    is_open=True,
    closed_at=None,
    quantity_remaining=Decimal(1)
)


@pytest.mark.parametrize(['expected_save_order_called', 'markets_order_info'],
    [
        (1, CLOSED_ORDER_INFO),
        (0, STILL_OPEN_ORDER_INFO),
    ]
)
def test_closes_open_orders_if_closed_on_market(expected_save_order_called: int, markets_order_info: OrderMarketInfo):
    candle_storage = flexmock()
    candle_storage.should_receive('mean').and_return(8000).and_return(7900)
    candle_storage.should_receive('get_last_minute_candle').and_return(flexmock(average_price=Decimal(Decimal(8000))))

    order_storage = create_order_storage_mock()
    order_storage.should_receive('find_by').and_return([DUMMY_OPEN_ORDER])
    order_storage.should_receive('delete')
    order_storage.should_receive('save_order').times(expected_save_order_called)

    market = create_market_mock()
    market.should_receive('get_order_status').and_return(markets_order_info).once()

    strategy = DoubleCrossoverStrategy(
        candle_storage,
        order_storage,
        create_event_emitter_mock(),
        CurrentUtcDateTimeFactory(),
        {
            'long_average_interval': 60 * 60,
            'short_average_interval': 15 * 60,
            'delay': 0,
            'number_of_runs': 1,
        }
    )
    strategy.run([market], BTC_USD_PAIR)


def create_market_mock() -> Union[Market, Mock]:
    market = flexmock(
        transaction_taker_fee=Decimal(0.0025),
        transaction_makerfee=Decimal(0.0025),
        name=DUMMY_MARKET_NAME
    )
    market.should_receive('calculate_maximal_amount_to_buy').and_return(Decimal(1))
    market.should_receive('calculate_maximal_amount_to_sell').and_return(Decimal(1))
    return market


def create_order_storage_mock() -> Union[OrderStorage, Mock]:
    order_storage = flexmock(name='yolo_order_storage')
    return order_storage


def create_event_emitter_mock() -> EventEmitter:
    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_order')
    return emitter_mock
