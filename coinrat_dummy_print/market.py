import uuid
from decimal import Decimal

from coinrat.domain import Market, Balance, Pair, Order, PairMarketInfo, \
    ORDER_TYPE_LIMIT, DIRECTION_SELL, DIRECTION_BUY, DateTimeFactory

MARKET_NAME = 'dummy_print'
DUMMY_STATIC_BALANCE = Decimal(0.5)


class PrintDummyMarket(Market):
    def __init__(self, datetime_factory: DateTimeFactory, name: str = MARKET_NAME) -> None:
        self._name = name
        self._datetime_factory = datetime_factory

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        return PairMarketInfo(pair, Decimal(0.004))

    @property
    def name(self) -> str:
        return self._name

    @property
    def transaction_fee(self) -> Decimal:
        return Decimal(0.0025)

    def get_balance(self, currency: str):
        return Balance(MARKET_NAME, currency, DUMMY_STATIC_BALANCE)

    def place_sell_order(self, order: Order) -> Order:
        print('Creating SELL order {}'.format(order))
        return order

    def place_buy_order(self, order: Order) -> Order:
        print('Creating BUY order {}'.format(order))
        return order

    def cancel_order(self, order_id: str) -> None:
        print('Cancelling order #{}'.format(order_id))
        pass

    def buy_max_available(self, pair: Pair) -> Order:
        print('BUYING max available for: {}'.format(pair))
        return self._create_fake_order(pair, DIRECTION_BUY)

    def sell_max_available(self, pair: Pair) -> Order:
        print('SELLING max available for: {}'.format(pair))
        return self._create_fake_order(pair, DIRECTION_SELL)

    def _create_fake_order(self, pair: Pair, direction: str) -> Order:
        return Order(
            uuid.uuid4(),
            self._name,
            direction,
            self._datetime_factory.now(),
            pair,
            ORDER_TYPE_LIMIT,
            Decimal(1),
            Decimal(8000)
        )
