import ccxt
from typing import Dict, List
from decimal import Decimal

from coinrat.domain import Balance
from coinrat.domain.number import to_decimal
from coinrat.domain.pair import Pair
from coinrat.domain.market import Market, PairMarketInfo
from coinrat.domain.order import Order, OrderMarketInfo

MARKET_NAME = 'cctx'


class CctxMarket(Market):
    def __init__(self, market_name: str) -> None:
        self._market_name = market_name
        self._exchange = getattr(ccxt, market_name)()

        self._makerFee = None
        self._takerFee = None

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {}

    @property
    def name(self) -> str:
        return self._market_name

    @property
    def transaction_taker_fee(self) -> Decimal:
        if self._makerFee is None:
            self.get_all_tradable_pairs()

        return self._makerFee

    @property
    def transaction_maker_fee(self) -> Decimal:
        if self._takerFee is None:
            self.get_all_tradable_pairs()

        return self._takerFee

    def get_balance(self, currency: str) -> Balance:
        pass

    def get_balances(self) -> List[Balance]:
        pass

    def get_current_price(self, pair: Pair) -> Decimal:
        pass

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        pass

    def place_order(self, order: Order) -> Order:
        pass

    def get_order_status(self, order: Order) -> OrderMarketInfo:
        pass

    def cancel_order(self, order_id: str) -> None:
        pass

    def get_all_tradable_pairs(self) -> List[Pair]:
        markets: Dict = self._exchange.load_markets()

        self._takerFee = Decimal('0')
        self._makerFee = Decimal('0')

        result = []
        for key, value in markets.items():
            maker = to_decimal(value['maker'])
            taker = to_decimal(value['taker'])

            self._takerFee = max(self._takerFee, maker)
            self._makerFee = max(self._makerFee, taker)

            result.append(Pair(value['quote'], value['base']))

        return result
