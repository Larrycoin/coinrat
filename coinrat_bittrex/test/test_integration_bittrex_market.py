import datetime

from decimal import Decimal

import pytest

from coinrat_bittrex.market import bittrex_market_factory
from coinrat.domain.pair import Pair, MarketPairDoesNotExistsException

BTC_USD_PAIR = Pair('USD', 'BTC')


def test_bittrex_static_data():
    synchronizer = bittrex_market_factory('', '')
    assert 'bittrex' == synchronizer.name
    assert Decimal('0.0025') == synchronizer.transaction_taker_fee


def test_get_pair_market_info():
    market_info = bittrex_market_factory('', '').get_pair_market_info(BTC_USD_PAIR)
    assert BTC_USD_PAIR == market_info.pair
    assert Decimal('0') < market_info.minimal_order_size


def test_get_pair_market_info_invalid_pair():
    with pytest.raises(MarketPairDoesNotExistsException):
        bittrex_market_factory('', '').get_pair_market_info(Pair('YOLO', 'SWAG'))


def test_get_last_minute_candle():
    now = datetime.datetime.now().astimezone(datetime.timezone.utc)

    candle = bittrex_market_factory('', '').get_last_minute_candles(BTC_USD_PAIR)[0]
    assert BTC_USD_PAIR == candle.pair
    assert now - datetime.timedelta(minutes=15) <= candle.time
    assert Decimal('0') < candle.open
    assert Decimal('0') < candle.high
    assert Decimal('0') < candle.low
    assert Decimal('0') < candle.close


def test_bittrex_get_current_price():
    price = bittrex_market_factory('', '').get_current_price(BTC_USD_PAIR)
    assert Decimal('0') < price


def test_get_candles():
    candles = bittrex_market_factory('', '').get_candles(BTC_USD_PAIR)
    assert 1000 < len(candles)
