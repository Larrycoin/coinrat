import datetime
from decimal import Decimal

from coinrat.domain.candle import Candle
from coinrat.domain import Pair


def test_candle():
    candle = Candle(
        '',
        Pair('USD', 'BTC'),
        datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        Decimal(1000),
        Decimal(2000),
        Decimal(3000),
        Decimal(4000)
    )

    assert '2017-01-01T00:00:00+00:00 O:1000.00000000 H:2000.00000000 L:3000.00000000 C:4000.00000000 ' + \
           '| CandleSize: 1-minute' == str(candle)
