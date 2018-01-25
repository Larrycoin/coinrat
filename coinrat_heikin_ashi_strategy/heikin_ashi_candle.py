import datetime
from decimal import Decimal

from coinrat.domain.candle import CandleSize, CANDLE_SIZE_UNIT_MINUTE


class HeikinAshiCandle:
    """
    1. HA-Close = (Open(0) + High(0) + Low(0) + Close(0)) / 4
    2. HA-Open = (HA-Open(-1) + HA-Close(-1)) / 2
    3. HA-High = Maximum of the High(0), HA-Open(0) or HA-Close(0)
    4. HA-Low = Minimum of the Low(0), HA-Open(0) or HA-Close(0)

    See: http://stockcharts.com/school/doku.php?id=chart_school:chart_analysis:heikin_ashi
    """

    def __init__(
            self,
            time: datetime.datetime,
            open_price: Decimal,
            high_price: Decimal,
            low_price: Decimal,
            close_price: Decimal,
            candle_size: CandleSize = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)
    ) -> None:
        assert isinstance(open_price, Decimal)
        assert isinstance(high_price, Decimal)
        assert isinstance(low_price, Decimal)
        assert isinstance(close_price, Decimal)

        candle_size.assert_candle_time(time)

        self.time = time
        self.open = open_price
        self.high = high_price
        self.low = low_price
        self.close = close_price
        self.candle_size = candle_size

    def __repr__(self):
        return '{0} O:{1:.8f} H:{2:.8f} L:{3:.8f} C:{4:.8f} | {5} (HeikinAshiCandle)' \
            .format(self.time.isoformat(), self.open, self.high, self.low, self.close, self.candle_size)
