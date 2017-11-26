import datetime
import logging
from typing import List, Union, Tuple

import pytest
from decimal import Decimal
from flexmock import flexmock, Mock

from coinrat.domain import Pair, Market, StrategyConfigurationException, NotEnoughBalanceToPerformOrderException
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy

BTC_USD_PAIR = Pair('USD', 'BTC')


@pytest.mark.parametrize(['error', 'markets'],
    [
        (True, []),
        (False, [flexmock()]),
        (True, [flexmock(), flexmock()]),
    ]
)
def test_number_of_markets_validation(error: bool, markets: List[Union[Market, Mock]]):
    candle_storage = flexmock().should_receive('mean').and_return(0).mock()

    if len(markets) == 1:  # Todo: Flexmock is not working properly with @pytest.mark.parametrize (MethodSignatureError)
        markets = [markets[0].should_receive('name').and_return('dummy_market_name').mock()]

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        candle_storage,
        mock_order_storage(),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=15),
        0,
        1
    )
    if error:
        with pytest.raises(StrategyConfigurationException):
            strategy.run(markets)
    else:
        strategy.run(markets)


@pytest.mark.parametrize(
    [
        'expected_buy',
        'expected_sell',
        'mean_evolution',
        'previous_order_quantity',
        'current_candle_average_price',
    ],
    [
        (0, 0, [(8000, 7800), (8000, 7900)], None, 7950),  # Short rise, but is still beneath long average
        (0, 0, [(8000, 7800), (8000, 7800)], None, 7750),  # Short lowers beneath long average
        (0, 0, [(8000, 8200), (8000, 8100)], None, 8050),  # Short lowers, but still uppers long average
        (0, 0, [(8000, 8100), (8000, 8200)], None, 8250),  # Short rise, uppers long

        (1, 0, [(8000, 7900), (8000, 8100)], None, 8150),  # Short rise, crossing long average
        (0, 1, [(8000, 8100), (8000, 7900)], None, 7850),  # Short lowers, crossing long average

        (0, 0, [(8000, 7999), (8000, 8001)], 7998, 8002),  # Short rise, crossing long average, but NOT WORTH IT
        (0, 0, [(8000, 8001), (8000, 7999)], 8002, 7998),  # Short lowers, crossing long average, but NOT WORTH IT

        (1, 0, [(8000, 7999), (8000, 8001)], 7998, 8050),  # Short rise, crossing long average, and WORTH IT
        (0, 1, [(8000, 8001), (8000, 7999)], 8002, 7950),  # Short lowers, crossing long average, and  WORTH IT

        (0, 0, [(8000, 8000), (8000, 8000)], None, 8000),  # Limit situations
        (0, 0, [(8000, 8000), (8000, 8001)], None, 8001),  #
        (0, 0, [(8000, 8001), (8000, 8000)], None, 8000),  #

        (0, 0, [(8000, 7999), (8000, 8000), (8000, 7999)], None, 7999),  # just touching the crossing
        (0, 0, [(8000, 8001), (8000, 8000), (8000, 8001)], None, 8001),  # just touching the crossing

        (1, 0, [(8000, 7999), (8000, 8000), (8000, 8001)], None, 8001),  # very smooth crossing in more steps
        (0, 1, [(8000, 8001), (8000, 8000), (8000, 7999)], None, 7999),  # very smooth crossing in more steps
    ]
)
def test_sending_signal(
    expected_buy: int,
    expected_sell: int,
    mean_evolution: List[Tuple[int, int]],
    previous_order_quantity: Union[int, None],
    current_candle_average_price: int
):
    candle_storage = flexmock()
    expectation = candle_storage.should_receive('mean')
    for mean in mean_evolution:
        expectation.and_return(mean[0]).and_return(mean[1])
    candle_storage.should_receive('get_current_candle').and_return(
        flexmock(average_price=Decimal(current_candle_average_price))
    )

    market = flexmock()
    market.should_receive('name').and_return('dummy_market_name')
    market.should_receive('buy_max_available').times(expected_buy)
    market.should_receive('sell_max_available').times(expected_sell)
    market.should_receive('transaction_fee').and_return(Decimal(0.0025))

    order_storage = flexmock()
    order_storage.should_receive('get_open_orders').and_return([])
    previous_order = None
    if previous_order_quantity is not None:
        previous_order = flexmock(quantity=Decimal(previous_order_quantity))
    order_storage.should_receive('find_last_order').and_return(previous_order)

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        candle_storage,
        order_storage,
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=15),
        0,
        len(mean_evolution)
    )
    strategy.run([market])


def test_not_enough_balance_logs_warning():
    candle_storage = flexmock()
    candle_storage.should_receive('mean').and_return(8000).and_return(7900).and_return(8000).and_return(8100)

    market = flexmock()
    market.should_receive('name').and_return('dummy_market_name')
    market.should_receive('buy_max_available').and_raise(NotEnoughBalanceToPerformOrderException)

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        candle_storage,
        mock_order_storage(),
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=15),
        0,
        2
    )
    flexmock(logging).should_receive('warning').once()
    strategy.run([market])


def mock_order_storage():
    mock = flexmock()
    mock.should_receive('get_open_orders').and_return([])
    mock.should_receive('find_last_order').and_return(None)

    return mock
