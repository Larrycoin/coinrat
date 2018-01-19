import datetime

from decimal import Decimal
from flexmock import flexmock

from coinrat_bittrex.synchronizer import BittrexSynchronizer
from coinrat.domain import Pair
from coinrat.domain.candle import MinuteCandle
from coinrat.event.event_emitter import EventEmitter

BTC_USD_PAIR = Pair('USD', 'BTC')
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

    synchronizer = BittrexSynchronizer(market, storage, create_emitter_mock(), delay=0, number_of_runs=1)
    synchronizer.synchronize(BTC_USD_PAIR)


def create_emitter_mock() -> EventEmitter:
    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_candles')
    emitter_mock.should_receive('emit_new_order')
    return emitter_mock
