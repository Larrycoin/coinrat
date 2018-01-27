import datetime

from decimal import Decimal

from coinrat.domain.pair import Pair
from coinrat.domain.candle import Candle
from coinrat_heikin_ashi_strategy.heikin_ashi_candle import create_initial_heikin_ashi_candle, candle_to_heikin_ashi, \
    HeikinAshiCandle

DUMMY_DATE = datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)


def test_create_initial_heikin_ashi_candle():
    candle = Candle(
        '',
        Pair('USD', 'BTC'),
        DUMMY_DATE,
        Decimal('2000'),
        Decimal('4500'),
        Decimal('1000'),
        Decimal('3000')
    )
    ha_candle = create_initial_heikin_ashi_candle(candle)
    assert str(ha_candle) == '2017-01-01T00:00:00+00:00 ' \
           + 'O:2500.00000000 H:4500.00000000 L:1000.00000000 C:2625.00000000 | CandleSize: 1-minute (Heikin-Ashi)'


def test_candle_to_heikin_ashi():
    previous_ha_candle = HeikinAshiCandle(
        '',
        Pair('USD', 'BTC'),
        DUMMY_DATE,
        Decimal('2500'),
        Decimal('4000'),
        Decimal('1000'),
        Decimal('2500'),
    )
    candle = Candle(
        '',
        Pair('USD', 'BTC'),
        DUMMY_DATE,
        Decimal('3000'),
        Decimal('3500'),
        Decimal('2500'),
        Decimal('4000')
    )
    current_ha_candle = candle_to_heikin_ashi(candle, previous_ha_candle)
    assert str(current_ha_candle) == '2017-01-01T00:00:00+00:00 ' \
           + 'O:2500.00000000 H:3500.00000000 L:2500.00000000 C:3250.00000000 | CandleSize: 1-minute (Heikin-Ashi)'
