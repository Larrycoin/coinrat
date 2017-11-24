import datetime
from typing import List, Union

import pytest
from flexmock import flexmock, Mock

from coinrat.domain import MarketPair, Market, StrategyConfigurationException
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy

BTC_USD_PAIR = MarketPair('USD', 'BTC')


def mock_storage(mean: int = 0):
    mock = flexmock()
    mock.should_receive('mean').and_return(mean)

    return mock


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
        mock_storage(),
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
