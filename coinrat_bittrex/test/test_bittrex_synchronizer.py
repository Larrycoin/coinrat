import datetime

from decimal import Decimal
from flexmock import flexmock

from coinrat_bittrex.synchronizer import BittrexSynchronizer
from coinrat.domain import MarketPair, MinuteCandle

BTC_USD_PAIR = MarketPair('USD', 'BTC')
DUMMY_CANDLE = MinuteCandle(
    '',
    BTC_USD_PAIR,
    datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
    Decimal(8000),
    Decimal(8000),
    Decimal(8000),
    Decimal(8000)
)


def test_synchronize_success():
    market = flexmock()
    market.should_receive('get_candles').and_return([DUMMY_CANDLE, DUMMY_CANDLE])
    market.should_receive('get_last_candle').and_return(DUMMY_CANDLE)

    storage = flexmock()
    storage.should_receive('write_candle').once()
    storage.should_receive('write_candles').once()

    synchronizer = BittrexSynchronizer(market, storage, 0, 1)
    synchronizer.synchronize(BTC_USD_PAIR)
