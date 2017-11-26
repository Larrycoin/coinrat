from decimal import Decimal
from typing import Union
from uuid import UUID

import datetime

from .coinrat import ForEndUserException
from .pair import Pair

ORDER_TYPE_LIMIT = 'limit'
ORDER_TYPE_MARKET = 'market'


class NotEnoughBalanceToPerformOrderException(ForEndUserException):
    pass


class Order:
    def __init__(
        self,
        order_id: UUID,
        market_name: str,
        created_at: datetime.datetime,
        pair: Pair,
        order_type: str,
        quantity: Decimal,
        rate: Union[Decimal, None] = None,
        market_id: Union[str, None] = None,
        is_open: bool = True
    ) -> None:
        assert '+00:00' in created_at.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(created_at.isoformat()))

        assert order_type in [ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET], 'Unknown type of order: "{}".'.format(order_type)
        assert isinstance(quantity, Decimal)

        if order_type == ORDER_TYPE_LIMIT:
            assert isinstance(rate, Decimal)
        if order_type == ORDER_TYPE_MARKET:
            assert rate is None, 'For market orders, rate must be None (does not make sense).'

        self._order_id = order_id
        self._market_name = market_name
        self._created_at = created_at
        self._pair = pair
        self._type = order_type
        self._quantity = quantity
        self._rate = rate
        self._id_on_market = market_id
        self._is_open = is_open

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def market_name(self) -> str:
        return self._market_name

    @property
    def created_at(self) -> datetime.datetime:
        return self._created_at

    @property
    def pair(self) -> Pair:
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

    @property
    def id_on_market(self) -> Union[str, None]:
        return self._id_on_market

    @property
    def is_open(self) -> bool:
        return self._is_open

    def set_id_on_market(self, id_on_market: str) -> None:
        self._id_on_market = id_on_market

    def __repr__(self) -> str:
        return (
            'Id: "{}, '
            + 'Market: "{}", '
            + 'Created: "{}, '
            + 'Open: "{}, '
            + '"ID on market: "{}", '
            + 'Pair: [{}], '
            + 'Type: "{}", '
            + 'Rate: {}, '
            + 'Quantity: {}'
        ).format(
            self._order_id,
            self._market_name,
            self._created_at.isoformat(),
            'OPEN' if self._is_open else 'CLOSED',
            self._id_on_market,
            self._pair,
            self._type,
            self._rate,
            self._quantity
        )


class OrderMarketInfo:
    def __init__(
        self,
        order: Order,
        is_open: bool,
        closed_at: Union[datetime.datetime, None],
        quantity_remaining: Decimal
    ) -> None:
        self._order = order
        self._is_open = is_open
        self._closed_at = closed_at
        self._quantity_remaining = quantity_remaining

    @property
    def order(self) -> Order:
        return self._order

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def closed_at(self) -> datetime.datetime:
        return self._closed_at

    @property
    def quantity_remaining(self) -> Decimal:
        return self._quantity_remaining
