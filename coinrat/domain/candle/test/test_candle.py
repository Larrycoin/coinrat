import datetime
from decimal import Decimal

from coinrat.domain.candle import Candle
from coinrat.domain import Pair

DUMMY_DATE = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)


def test_candle():
    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('1000'), Decimal('2000'), Decimal('3000'), Decimal('4000'))
    assert '2017-01-01T00:00:00+00:00 O:1000.00000000 H:2000.00000000 L:3000.00000000 C:4000.00000000 ' + \
           '| CandleSize: 1-minute' == str(candle)

    assert candle.is_bearish() is False
    assert candle.is_bullish() is True


def test_bearish_bullish():
    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('1000'), Decimal('2000'), Decimal('3000'), Decimal('4000'))
    assert candle.is_bearish() is False
    assert candle.is_bullish() is True

    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('8000'), Decimal('2000'), Decimal('3000'), Decimal('4000'))
    assert candle.is_bearish() is True
    assert candle.is_bullish() is False

    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('8000'), Decimal('10000'), Decimal('5000'), Decimal('8000'))
    assert candle.is_bearish() is False
    assert candle.is_bullish() is False


def test_candle_body_size():
    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('1000'), Decimal('2000'), Decimal('3000'), Decimal('4000'))
    assert candle.body_size() == Decimal('3000')

    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('8000'), Decimal('2000'), Decimal('3000'), Decimal('4000'))
    assert candle.body_size() == Decimal('4000')

    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('8000'), Decimal('10000'), Decimal('5000'), Decimal('8000'))
    assert candle.body_size() == Decimal('0')


def test_candle_wicks():
    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('8000'), Decimal('10000'), Decimal('5000'), Decimal('8000'))
    assert candle.has_upper_wick() is True
    assert candle.has_lower_wick() is True

    candle = Candle('', Pair('USD', 'BTC'), DUMMY_DATE, Decimal('8000'), Decimal('8000'), Decimal('8000'), Decimal('8000'))
    assert candle.has_upper_wick() is False
    assert candle.has_lower_wick() is False
