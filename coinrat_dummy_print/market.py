import uuid
from decimal import Decimal
from typing import Dict

from coinrat.domain import Market, Balance, Pair, PairMarketInfo, DateTimeFactory
from coinrat.domain.order import ORDER_TYPE_LIMIT, DIRECTION_SELL, DIRECTION_BUY, Order, OrderMarketInfo, \
    ORDER_STATUS_CLOSED

MARKET_NAME = 'dummy_print'
DUMMY_STATIC_BALANCE = Decimal(0.5)
DUMMY_QUANTITY = Decimal(1)


class PrintDummyMarket(Market):

    def __init__(self, datetime_factory: DateTimeFactory, configuration: Dict) -> None:
        self._name = configuration['mocked_market_name'] if 'mocked_market_name' in configuration else MARKET_NAME
        self._datetime_factory = datetime_factory

    @staticmethod
    def get_configuration_structure() -> Dict:
        return {'mocked_market_name': str}

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        return PairMarketInfo(pair, Decimal(0.004))

    def get_order_status(self, order: Order) -> OrderMarketInfo:
        return OrderMarketInfo(order, True, None, DUMMY_QUANTITY)

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
        created_at = self._datetime_factory.now()
        return Order(
            uuid.uuid4(),
            self._name,
            direction,
            created_at,
            pair,
            ORDER_TYPE_LIMIT,
            DUMMY_QUANTITY,
            Decimal(8000),
            status=ORDER_STATUS_CLOSED,
            closed_at=created_at
        )
