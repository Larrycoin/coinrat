import uuid
from decimal import Decimal
from typing import Dict, List

from coinrat.domain import Market, Balance, Pair, PairMarketInfo, DateTimeFactory
from coinrat.domain.order import ORDER_TYPE_LIMIT, DIRECTION_SELL, DIRECTION_BUY, Order, OrderMarketInfo, \
    ORDER_STATUS_CLOSED

MARKET_NAME = 'mock'
DUMMY_STATIC_BALANCE = Decimal(0.5)
DUMMY_QUANTITY = Decimal(1)

DEFAULT_TRANSACTION_FEE = Decimal(0.0025)


class MockMarket(Market):

    def __init__(self, datetime_factory: DateTimeFactory, configuration: Dict) -> None:
        self._name = configuration['mocked_market_name'] if 'mocked_market_name' in configuration else MARKET_NAME

        self._transaction_fee = configuration['mocked_transaction_fee'] \
            if 'mocked_transaction_fee' in configuration \
            else DEFAULT_TRANSACTION_FEE

        self._datetime_factory = datetime_factory

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {
            'mocked_market_name': {
                'type': 'string',
                'title': 'Mocked Market Name',
            },
            'mocked_transaction_fee': {
                'type': 'Decimal',
                'title': 'Transaction Fee',
            },
        }

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        return PairMarketInfo(pair, Decimal(0.004))

    def get_order_status(self, order: Order) -> OrderMarketInfo:
        return OrderMarketInfo(order, True, None, DUMMY_QUANTITY)

    @property
    def name(self) -> str:
        return self._name

    @property
    def transaction_fee(self) -> Decimal:
        return self._transaction_fee

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

    def get_all_tradable_pairs(self) -> List[Pair]:
        return [
            Pair('USD', 'BTC'),
            Pair('USD', 'LTC'),
            Pair('USD', 'ETH'),
            Pair('USD', 'XMR'),

            Pair('BTC', 'LTC'),
            Pair('BTC', 'ETH'),
            Pair('BTC', 'XMR'),
        ]

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
