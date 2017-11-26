import uuid
from decimal import Decimal

import datetime

from coinrat.domain import Market, Balance, Pair, Order, PairMarketInfo, ORDER_TYPE_LIMIT

MARKET_NAME = 'dummy_print'
DUMMY_STATIC_BALANCE = Decimal(0.5)


class PrintDummyMarket(Market):
    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        return PairMarketInfo(pair, Decimal(0.004))

    def name(self) -> str:
        return MARKET_NAME

    @property
    def transaction_fee_coefficient(self) -> Decimal:
        return Decimal(0.0025)

    def get_balance(self, currency: str):
        return Balance(MARKET_NAME, currency, DUMMY_STATIC_BALANCE)

    def create_sell_order(self, order: Order) -> Order:
        print('Creating SELL order {}'.format(order))
        return order

    def create_buy_order(self, order: Order) -> Order:
        print('Creating BUY order {}'.format(order))
        return order

    def cancel_order(self, order_id: str) -> None:
        print('Cancelling order #{}'.format(order_id))
        pass

    def buy_max_available(self, pair: Pair) -> Order:
        print('BUYING max available for: {}'.format(pair))
        return self._create_fake_order(pair)

    def sell_max_available(self, pair: Pair) -> Order:
        print('SELLING max available for: {}'.format(pair))
        return self._create_fake_order(pair)

    @staticmethod
    def _create_fake_order(pair: Pair) -> Order:
        return Order(
            uuid.uuid4(),
            MARKET_NAME,
            datetime.datetime.now().astimezone(datetime.timezone.utc),
            pair,
            ORDER_TYPE_LIMIT,
            Decimal(1),
            Decimal(8000)
        )
