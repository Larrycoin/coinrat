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
        return super().__repr__() + ' (HeikinAshiCandle)'
