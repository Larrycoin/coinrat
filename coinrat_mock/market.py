import uuid
from decimal import Decimal
from typing import Dict, List

from coinrat.domain import Market, Balance, Pair, PairMarketInfo, DateTimeFactory
from coinrat.domain.order import ORDER_TYPE_LIMIT, DIRECTION_SELL, DIRECTION_BUY, Order, OrderMarketInfo
from coinrat.domain.configuration_structure import CONFIGURATION_STRUCTURE_TYPE_STRING, \
    CONFIGURATION_STRUCTURE_TYPE_DECIMAL
from domain.order import ORDER_TYPE_MARKET

MARKET_NAME = 'mock'
DEFAULT_BASE_BALANCE = Decimal(1000)
DEFAULT_TRANSACTION_FEE = Decimal(0.0025)


class MockMarket(Market):
    def __init__(self, datetime_factory: DateTimeFactory, configuration: Dict) -> None:
        self._name = configuration['mocked_market_name'] if 'mocked_market_name' in configuration else MARKET_NAME
        self._mocked_base_currency_balance: Decimal = configuration['mocked_base_currency_balance'] \
            if 'mocked_base_currency_balance' in configuration \
            else DEFAULT_BASE_BALANCE

        self._transaction_maker_fee: Decimal = configuration['mocked_transaction_maker_fee'] \
            if 'mocked_transaction_fee' in configuration \
            else DEFAULT_TRANSACTION_FEE

        self._transaction_taker_fee: Decimal = configuration['mocked_transaction_taker_fee'] \
            if 'mocked_transaction_taker_fee' in configuration \
            else DEFAULT_TRANSACTION_FEE

        self._datetime_factory = datetime_factory
        self._balances: Dict[str, Decimal] = {}

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {
            'mocked_market_name': {
                'type': CONFIGURATION_STRUCTURE_TYPE_STRING,
                'title': 'Mocked Market Name',
                'default': 'bittrex',
            },
            'mocked_base_currency_balance': {
                'type': CONFIGURATION_STRUCTURE_TYPE_DECIMAL,
                'title': 'Mocked balance',
                'description': 'Balance for selected pair, that will be available for strategy on mocked market.',
                'default': '0.5',
                'unit': 'market currency',
            },
            'mocked_transaction_maker_fee': {
                'type': CONFIGURATION_STRUCTURE_TYPE_DECIMAL,
                'title': 'Maker Fee',
                'description': 'Transaction fee that will be charged when you add the stock (usually all LIMIT orders).',
                'default': str(DEFAULT_TRANSACTION_FEE),
                'unit': 'percents',
            },
            'mocked_transaction_taker_fee': {
                'type': CONFIGURATION_STRUCTURE_TYPE_DECIMAL,
                'title': 'Taker Fee',
                'description':
                    'Transaction fee that will be charged when you reduce stock by you action (usually MARKET orders).',
                'default': '0.004',
                'unit': 'percents',
            },
        }

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        return PairMarketInfo(pair, Decimal(0.004))

    def get_order_status(self, order: Order) -> OrderMarketInfo:
        return OrderMarketInfo(order, is_open=order.is_open, closed_at=order.closed_at, quantity_remaining=Decimal(0))

    @property
    def name(self) -> str:
        return self._name

    @property
    def transaction_fee(self) -> Decimal:
        return self._transaction_taker_fee

    def get_balance(self, currency: str) -> Balance:
        return Balance(MARKET_NAME, currency, self._balances[currency])

    def place_sell_order(self, order: Order) -> Order:
        self._process_order(order)
        return order

    def place_buy_order(self, order: Order) -> Order:
        self._process_order(order)
        return order

    def cancel_order(self, order_id: str) -> None:
        pass

    def buy_max_available(self, pair: Pair) -> Order:
        order = self._create_fake_order(pair, DIRECTION_BUY, rate)
        self._process_order(order)
        return order

    def sell_max_available(self, pair: Pair) -> Order:
        order = self._create_fake_order(pair, DIRECTION_SELL, rate)
        self._process_order(order)
        return order

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

    def _create_fake_order(self, pair: Pair, direction: str, rate) -> Order:
        self.initialize_balances_if_not_yet(pair)

        if direction == DIRECTION_SELL:
            quantity = self.get_balance(pair.market_currency).available_amount

        elif direction == DIRECTION_SELL:
            quantity = self.calculate_maximal_amount_to_by(pair, rate)

        else:
            raise ValueError('{} is not valid order direction'.format(direction))

        created_at = self._datetime_factory.now()

        return Order(
            uuid.uuid4(),
            self._name,
            direction,
            created_at,
            pair,
            ORDER_TYPE_LIMIT,
            quantity,
            rate
        )

    def initialize_balances_if_not_yet(self, pair: Pair) -> None:
        if pair.base_currency not in self._balances and pair.market_currency not in self._balances:
            self._balances[pair.base_currency] = self._mocked_base_currency_balance
            self._balances[pair.market_currency] = 0

    def _process_order(self, order: Order) -> None:
        order.close(order.created_at)

        fee = self.calculate_fee(order)

        if order.is_sell():
            self._balances[order.pair.base_currency] += order.quantity * order.rate * (1 - fee)
            self._balances[order.pair.market_currency] -= order.quantity

        elif order.is_buy():
            self._balances[order.pair.base_currency] -= order.quantity * order.rate
            self._balances[order.pair.market_currency] -= order.quantity * (1 - fee)

    def calculate_fee(self, order: Order):
        if order.type == ORDER_TYPE_LIMIT:
            return self._transaction_maker_fee

        elif order.type == ORDER_TYPE_MARKET:
            return self._transaction_taker_fee

        raise ValueError('{} is not valid order type'.format(order.type))
