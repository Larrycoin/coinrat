import datetime
from typing import List, Union

import pytest
from flexmock import flexmock, Mock

from coinrat.domain import MarketPair, Market, StrategyConfigurationException
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy

BTC_USD_PAIR = MarketPair('USD', 'BTC')


@pytest.mark.parametrize(['error', 'markets'],
    [
        (True, []),
        (False, [flexmock()]),
        (True, [flexmock(), flexmock()]),
    ]
)
def test_number_of_markets_validation(error: bool, markets: List[Union[Market, Mock]]):
    if len(markets) == 1:  # Todo: Flexmock is not working properly with @pytest.mark.parametrize (MethodSignatureError)
        markets = [markets[0].should_receive('get_name').and_return('dummy_market_name').mock()]

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        flexmock().should_receive('mean').and_return(0),
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


@pytest.mark.parametrize([
    'expected_buy',
    'expected_sell',
    'first_long_mean',
    'second_long_mean',
    'first_short_mean',
    'second_short_mean',
],
    [
        (0, 0, 8000, 8000, 7800, 7900),  # Short average rise, but is still beneath long average
        (0, 0, 8000, 8000, 7800, 7800),  # Short average lowers beneath long average
    ]
)
def test_sending_signal(
    expected_buy: int,
    expected_sell: int,
    first_long_mean: int,
    second_long_mean: int,
    first_short_mean: int,
    second_short_mean: int
):
    storage = flexmock()
    storage.should_receive('mean').and_return().and_return()

    market = flexmock()
    market.should_receive('get_name').and_return('dummy_market_name').mock()
    market.should_receive('buy_max_available').times(0)
    market.should_receive('sell_max_available').times(0)

    strategy = DoubleCrossoverStrategy(
        BTC_USD_PAIR,
        storage,
        datetime.timedelta(hours=1),
        datetime.timedelta(minutes=15),
        0,
        2
    )
    strategy.run([market])
