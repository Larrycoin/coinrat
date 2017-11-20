from decimal import Decimal

import datetime
from typing import Union

ORDER_TYPE_LIMIT = 'limit'
ORDER_TYPE_MARKET = 'market'


class Balance:
    def __init__(self, currency: str, available_amount: Decimal) -> None:
        assert isinstance(available_amount, Decimal)

        self._currency = currency
        self._available_amount = available_amount

    @property
    def currency(self):
        return self._currency

    @property
    def available_amount(self) -> Decimal:
        return self._available_amount

    def __repr__(self):
        return '{0:.8f} {1}'.format(self._available_amount, self._currency)


class Candle:
    def __init__(self, time: datetime.datetime, bid_price: Decimal, ask_price: Decimal) -> None:
        """
        :param bid_price Buyers are willing to buy for such a price
        :param ask_price Sellers are asking for such a price
        """
        assert isinstance(ask_price, Decimal)
        assert isinstance(bid_price, Decimal)

        self._time = time
        self._bid_price = bid_price
        self._ask_price = ask_price

    @property
    def time(self) -> datetime.datetime:
        return self._time

    @property
    def bid_price(self) -> Decimal:
        return self._bid_price

    @property
    def ask_price(self) -> Decimal:
        return self._ask_price

    @property
    def average_price(self) -> Decimal:
        return (self._bid_price + self._ask_price) / 2

    def __repr__(self):
        return '{0} {1:.8f} {2:.8f}'.format(self._time.isoformat(), self._bid_price, self._ask_price)


class MarketPair:
    def __init__(self, left: str, right: str) -> None:
        self._left = left
        self._right = right

    @property
    def left(self) -> str:
        return self._left

    @property
    def right(self) -> str:
        return self._right

    def __repr__(self):
        return '{}-{}'.format(self._left, self._right)


class Order:
    def __init__(self, pair: MarketPair, order_type: str, quantity: Decimal, rate: Union[Decimal, None] = None) -> None:
        assert order_type in [ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET]
        assert isinstance(quantity, Decimal)

        if order_type == ORDER_TYPE_LIMIT:
            assert isinstance(rate, Decimal)
        if order_type == ORDER_TYPE_MARKET:
            assert rate is None

        self._pair = pair
        self._type = order_type
        self._quantity = quantity
        self._rate = rate

    @property
    def pair(self) -> MarketPair:
        return self._pair

    @property
    def type(self) -> str:
        return self._type

    @property
    def rate(self) -> Union[Decimal, None]:
        return self._rate

    @property
    def quantity(self) -> Decimal:
        return self._quantity
