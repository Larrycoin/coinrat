import pytest
from flexmock import flexmock

from coinrat_cryptocompare.synchronizer import CryptocompareSynchronizer, CryptocompareRequestException
from coinrat.domain.pair import Pair
from coinrat.event.event_emitter import EventEmitter

BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_CANDLE_DATA = [
    {
        'time': 1511608020,
        'close': 8403.35,
        'high': 8403.35,
        'low': 8403,
        'open': 8403,
        'volumefrom': 1.09,
        'volumeto': 9197.77
    }, {
        'time': 1511608080,
        'close': 8403.35,
        'high': 8403.35,
        'low': 8403.35,
        'open': 8403.35,
        'volumefrom': 0,
        'volumeto': 0
    }
]


def test_synchronize_success():
    response = flexmock(status_code=200)
    response.should_receive('json').and_return({'Response': 'Success', 'Data': DUMMY_CANDLE_DATA})
    synchronizer = CryptocompareSynchronizer(
        'bittrex',
        mock_storage(1),
        create_event_emitter_mock(),
        mock_session(response),
        delay=0,
        number_of_runs=1
    )
    synchronizer.synchronize(BTC_USD_PAIR)


def mock_session(response):
    session = flexmock()
    session.should_receive('get').and_return(response).once()
    return session


def test_synchronize_invalid_response_code():
    response = flexmock(status_code=400)
    response.should_receive('text').and_return('')
    synchronizer = create_synchronizer_with_no_retries(response)

    with pytest.raises(CryptocompareRequestException):
        synchronizer.synchronize(BTC_USD_PAIR)


def test_synchronize_response_field_indicates_error():
    response = flexmock(status_code=200)
    response.should_receive('json').and_return({'Response': 'Error', 'Data': []})
    response.should_receive('text').and_return('')
    synchronizer = create_synchronizer_with_no_retries(response)

    with pytest.raises(CryptocompareRequestException):
        synchronizer.synchronize(BTC_USD_PAIR)


def create_synchronizer_with_no_retries(response):
    emitter_mock = create_event_emitter_mock()
    synchronizer = CryptocompareSynchronizer(
        'bittrex',
        mock_storage(0),
        emitter_mock,
        mock_session(response),
        delay=0,
        number_of_runs=1,
        time_to_sleep_after_error=0,
        max_number_of_retries=0
    )
    return synchronizer


def create_event_emitter_mock() -> EventEmitter:
    emitter_mock = flexmock()
    emitter_mock.should_receive('emit_new_candles')
    return emitter_mock


def mock_storage(write_candles_call_count: int):
    storage = flexmock(name='yolo_storage')
    storage.should_receive('write_candles').times(write_candles_call_count)

    return storage
