import datetime

from decimal import Decimal
from flexmock import flexmock

from coinrat.domain.market import MarketException
from coinrat_bittrex.synchronizer import BittrexSynchronizer
from coinrat.domain.pair import Pair
from coinrat.domain.candle import Candle
from coinrat.event.event_emitter import EventEmitter

BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_CANDLE = Candle(
    '',
    BTC_USD_PAIR,
    datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
    Decimal('8000'),
    Decimal('8000'),
    Decimal('8000'),
    Decimal('8000')
)


def test_synchronize_success():
    market = flexmock(name='yolo_market')
    market.should_receive('get_candles').and_return([DUMMY_CANDLE, DUMMY_CANDLE])
    market.should_receive('get_last_minute_candles').and_return(DUMMY_CANDLE)

    storage = flexmock(name='yolo_storage')
    storage.should_receive('write_candles').times(2)

    synchronizer = BittrexSynchronizer(market, storage, create_emitter_mock(), delay=0, number_of_runs=1)
    synchronizer.synchronize(BTC_USD_PAIR)


def test_synchronize_recover_from_error():
    market = flexmock(name='yolo_market')
    market.should_receive('get_candles').and_return([]).times(2)
    market.should_receive('get_last_minute_candles').and_raise(MarketException()).times(1)

    storage = flexmock(name='yolo_storage')
    storage.should_receive('write_candles')

    synchronizer = BittrexSynchronizer(market, storage, create_emitter_mock(), delay=0, number_of_runs=3)
    synchronizer.synchronize(BTC_USD_PAIR)


def create_emitter_mock() -> EventEmitter:
    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_candles')
    emitter_mock.should_receive('emit_new_order')
    return emitter_mock
