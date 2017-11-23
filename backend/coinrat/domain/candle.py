import datetime

from decimal import Decimal

from .pair import MarketPair


class MinuteCandle:
    """
    OPEN, CLOSE: The open and close prices are the first and last transaction prices for that time period (minute).

    LOW, HIGH: The high price is the highest price reached during a specific time period. The low price is the lowest
    price reached during a specific period (minute).
    """

    def __init__(
        self,
        market_name: str,
        pair: MarketPair,
        time: datetime.datetime,
        open_price: Decimal,
        close_price: Decimal,
        low_price: Decimal,
        high_price: Decimal
    ) -> None:
        assert isinstance(open_price, Decimal)
        assert isinstance(close_price, Decimal)
        assert isinstance(low_price, Decimal)
        assert isinstance(high_price, Decimal)

        assert time.second == 0
        assert time.microsecond == 0

        assert '+00:00' in time.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(time.isoformat()))

        self._market_name = market_name
        self._pair = pair
        self._time = time
        self._open = open_price
        self._close = close_price
        self._low = low_price
        self._high = high_price

    @property
    def pair(self) -> MarketPair:
        return self._pair

    @property
    def market_name(self) -> str:
        return self._market_name

    @property
    def time(self) -> datetime.datetime:
        return self._time

    @property
    def open(self) -> Decimal:
        return self._open

    @property
    def close(self) -> Decimal:
        return self._close

    @property
    def low(self) -> Decimal:
        return self._low

    @property
    def high(self) -> Decimal:
        return self._high

    @property
    def average_price(self) -> Decimal:
        return (self._low + self._high) / 2

    def __repr__(self):
        return '{0} O:{1:.8f} C:{2:.8f} L:{3:.8f} H:{2:.8f}' \
            .format(self._time.isoformat(), self._open, self._close, self._low, self._high)
