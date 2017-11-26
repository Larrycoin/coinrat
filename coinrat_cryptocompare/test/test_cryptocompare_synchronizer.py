import pytest
from flexmock import flexmock

from coinrat_cryptocompare.synchronizer import CryptocompareSynchronizer, CryptocompareRequestException
from coinrat.domain import Pair

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
    synchronizer = CryptocompareSynchronizer('bittrex', mock_storage(1), mock_session(response), 0, 1)
    synchronizer.synchronize(BTC_USD_PAIR)


def mock_session(response):
    session = flexmock()
    session.should_receive('get').and_return(response).once()
    return session


def test_synchronize_invalid_response_code():
    response = flexmock(status_code=400)
    response.should_receive('text').and_return('')
    synchronizer = CryptocompareSynchronizer('bittrex', mock_storage(0), mock_session(response), 0, 1)

    with pytest.raises(CryptocompareRequestException):
        synchronizer.synchronize(BTC_USD_PAIR)


def test_synchronize_response_field_indicates_error():
    response = flexmock(status_code=200)
    response.should_receive('json').and_return({'Response': 'Error', 'Data': []})
    response.should_receive('text').and_return('')
    synchronizer = CryptocompareSynchronizer('bittrex', mock_storage(0), mock_session(response), 0, 1)

    with pytest.raises(CryptocompareRequestException):
        synchronizer.synchronize(BTC_USD_PAIR)


def mock_storage(write_candles_call_count: int):
    storage = flexmock()
    storage.should_receive('write_candles').times(write_candles_call_count)

    return storage
