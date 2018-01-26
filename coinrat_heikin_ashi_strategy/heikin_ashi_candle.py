import numpy

from coinrat.domain.candle import Candle


class HeikinAshiCandle(Candle):
    """
    1. HA-Close = (Open(0) + High(0) + Low(0) + Close(0)) / 4
    2. HA-Open = (HA-Open(-1) + HA-Close(-1)) / 2
    3. HA-High = Maximum of the High(0), HA-Open(0) or HA-Close(0)
    4. HA-Low = Minimum of the Low(0), HA-Open(0) or HA-Close(0)

    See: http://stockcharts.com/school/doku.php?id=chart_school:chart_analysis:heikin_ashi
    """

    def __repr__(self):
        return super().__repr__() + ' (Heikin-Ashi)'


def create_initial_heikin_ashi_candle(candle: Candle) -> HeikinAshiCandle:
    """
    As Heikin-Ashi candle refers to previous candle we have chicken-egg problem here.
    Thi method is used to construct first candle in the series.
    """
    return HeikinAshiCandle(
        candle.market_name,
        candle.pair,
        candle.time,
        open_price=(candle.open + candle.high + candle.low + candle.close) / 4,
        high_price=candle.high,
        low_price=candle.low,
        close_price=(candle.open + candle.close) / 2,
        candle_size=candle.candle_size
    )


def candle_to_heikin_ashi(candle: Candle, previous: HeikinAshiCandle) -> HeikinAshiCandle:
    heikin_close = (candle.open + candle.high + candle.low + candle.close) / 4
    heikin_open = (previous.open + previous.close) / 2
    elements = numpy.array([candle.high, candle.low, heikin_open, heikin_close])
    heikin_high = elements.max(0)
    heikin_low = elements.min(0)

    return HeikinAshiCandle(
        candle.market_name,
        candle.pair,
        candle.time,
        heikin_close,
        heikin_high,
        heikin_low,
        heikin_open,
        candle.candle_size
    )
