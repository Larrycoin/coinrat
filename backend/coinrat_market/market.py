from decimal import Decimal

import datetime


class Balance:
    def __init__(self, currency: str, available_amount: Decimal) -> None:
        super().__init__()
        assert isinstance(available_amount, Decimal)

        self._currency = currency
        self._available_amount = available_amount

    def get_currency(self):
        return self._currency

    def get_available_amount(self) -> Decimal:
        return self._available_amount

    def __repr__(self):
        return '{0:.8f} {1}'.format(self._available_amount, self._currency)


class Candle:
    def __init__(self, time: datetime.time, low: Decimal, high: Decimal) -> None:
        super().__init__()

        assert isinstance(high, Decimal)
        assert isinstance(low, Decimal)

        self._time = time
        self._low = low
        self._high = high

    def get_time(self) -> datetime.time:
        return self._time

    def get_high(self) -> Decimal:
        return self._high

    def get_low(self) -> Decimal:
        return self._low

    def __repr__(self):
        return '{0} {1:.8f} {2:.8f}'.format(self._time.isoformat(), self._low, self._high)
