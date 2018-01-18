from decimal import Decimal
from typing import Dict, List

from coinrat.domain import Market, Balance, Pair, PairMarketInfo, DateTimeFactory
from coinrat.domain.order import ORDER_TYPE_LIMIT, Order, OrderMarketInfo, ORDER_TYPE_MARKET
from coinrat.domain.configuration_structure import CONFIGURATION_STRUCTURE_TYPE_STRING, \
    CONFIGURATION_STRUCTURE_TYPE_DECIMAL

MARKET_NAME = 'mock'
DEFAULT_BASE_BALANCE = Decimal(1000)
DEFAULT_TRANSACTION_FEE = Decimal(0.0025)
DEFAULT_BASE_CURRENCY = 'USD'


class MockMarket(Market):

    def __init__(self, datetime_factory: DateTimeFactory, configuration: Dict) -> None:
        self._name = configuration['mocked_market_name'] if 'mocked_market_name' in configuration else MARKET_NAME

        mocked_base_currency_balance: Decimal = configuration['mocked_base_currency_balance'] \
            if 'mocked_base_currency_balance' in configuration \
            else DEFAULT_BASE_BALANCE

        mocked_base_currency: Decimal = configuration['mocked_base_currency'] \
            if 'mocked_base_currency' in configuration \
            else DEFAULT_BASE_CURRENCY

        self._transaction_maker_fee: Decimal = configuration['mocked_transaction_maker_fee'] \
            if 'mocked_transaction_fee' in configuration \
            else DEFAULT_TRANSACTION_FEE

        self._transaction_taker_fee: Decimal = configuration['mocked_transaction_taker_fee'] \
            if 'mocked_transaction_taker_fee' in configuration \
            else DEFAULT_TRANSACTION_FEE

        self._datetime_factory = datetime_factory
        self._balances: Dict[str, Decimal] = {mocked_base_currency: mocked_base_currency_balance}

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {
            'mocked_market_name': {
                'type': CONFIGURATION_STRUCTURE_TYPE_STRING,
                'title': 'Mocked Market Name',
                'default': 'bittrex',
            },
            'mocked_base_currency': {
                'type': CONFIGURATION_STRUCTURE_TYPE_STRING,
                'title': 'Base currency',
                'default': DEFAULT_BASE_CURRENCY,
                'unit': '',
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
    def transaction_taker_fee(self) -> Decimal:
        return self._transaction_taker_fee

    @property
    def transaction_maker_fee(self):
        return self._transaction_maker_fee

    def get_balance(self, currency: str) -> Balance:
        if currency not in self._balances:
            self._balances[currency] = Decimal(0)

        return Balance(MARKET_NAME, currency, self._balances[currency])

    def place_order(self, order: Order) -> Order:
        self._process_order(order)
        return order

    def cancel_order(self, order_id: str) -> None:
        pass

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

    def _process_order(self, order: Order) -> None:
        order.close(order.created_at)

        fee = self.calculate_fee(order)

        if order.pair.base_currency not in self._balances:
            self._balances[order.pair.base_currency] = Decimal(0)

        if order.pair.market_currency not in self._balances:
            self._balances[order.pair.market_currency] = Decimal(0)

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
