from decimal import Decimal
from typing import Union, Dict, List

from coinrat.domain import Balance
from .order import Order, OrderMarketInfo
from .pair import Pair


class MarketOrderException(Exception):
    pass


class PairMarketInfo:
    def __init__(self, pair: Pair, minimal_order_size: Union[Decimal, None]) -> None:
        self._pair = pair
        self._minimal_order_size = minimal_order_size

    @property
    def pair(self):
        return self._pair

    @property
    def minimal_order_size(self):
        return self._minimal_order_size

    def __repr__(self) -> str:
        return 'Pair: [{0}], minimal order size: {1:.8}'.format(self._pair, self._minimal_order_size)


class Market:
    @property
    def name(self) -> str:
        raise NotImplementedError()

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        raise NotImplementedError()

    @property
    def transaction_taker_fee(self):
        raise NotImplementedError()

    @property
    def transaction_maker_fee(self):
        raise NotImplementedError()

    def get_balance(self, currency: str) -> Balance:
        raise NotImplementedError()

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        raise NotImplementedError()

    def place_order(self, order: Order) -> Order:
        raise NotImplementedError()

    def get_order_status(self, order: Order) -> OrderMarketInfo:
        raise NotImplementedError()

    def cancel_order(self, order_id: str) -> None:
        raise NotImplementedError()

    def get_all_tradable_pairs(self) -> List[Pair]:
        raise NotImplementedError()

    def __repr__(self) -> str:
        return self.name

    def calculate_maximal_amount_to_buy(self, pair: Pair, current_price: Decimal) -> Decimal:
        return self.get_balance(pair.base_currency).available_amount / current_price

    def calculate_maximal_amount_to_sell(self, pair: Pair) -> Decimal:
        return self.get_balance(pair.market_currency).available_amount
