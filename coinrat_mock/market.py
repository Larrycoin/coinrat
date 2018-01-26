from decimal import Decimal
from typing import Dict, List

from coinrat.domain import Market, Balance, Pair, PairMarketInfo, DateTimeFactory, serialize_pair
from coinrat.domain.order import ORDER_TYPE_LIMIT, Order, OrderMarketInfo, ORDER_TYPE_MARKET, \
    NotEnoughBalanceToPerformOrderException
from coinrat.domain.configuration_structure import CONFIGURATION_STRUCTURE_TYPE_STRING, \
    CONFIGURATION_STRUCTURE_TYPE_DECIMAL

MARKET_NAME = 'mock'
DEFAULT_BASE_BALANCE = Decimal('1000')
DEFAULT_TRANSACTION_FEE = Decimal('0.0025')
DEFAULT_BASE_CURRENCY = 'USD'


class MockMarket(Market):
    """
    Market class that imitates stock-market behaviour. And is mend for testing your strategies.

    Configuration example:

        {
            'mocked_market_name': 'Bitfinex',  # Name of the market you are mocking,
                                               # used for linking to the candle and order data in the storages

            'mocked_base_currency_balance': '1000',  # Place 1000$ on the market at beginning
            'mocked_base_currency': 'USD',  # Base currency can be changed different currency

            # When you place a order that gets compeltely filled immediately
            # (for example with market and stop orders) you are a “taker” and you pay a fee for this.

            # Meanwhile, if an order takes a while to fill (such as with a limit order for a price the coin won’t
            # hit immediately) you are a “maker” and you generally pay a reduced fee for this.

            # For more, see: http://cryptocurrencyfacts.com/maker-vs-taker-cryptocurrency/

            'mocked_transaction_taker_fee': Decimal('0.0025'),
            'mocked_transaction_maker_fee': Decimal('0.001'),
        }

    """

    def __init__(self, datetime_factory: DateTimeFactory, configuration: Dict) -> None:
        self._datetime_factory = datetime_factory
        self._name = MARKET_NAME
        self._transaction_maker_fee: Decimal = DEFAULT_TRANSACTION_FEE
        self._transaction_taker_fee: Decimal = DEFAULT_TRANSACTION_FEE
        self._balances: Dict[str, Decimal] = {}
        self._current_prices: Dict[str, Decimal] = {}

        self.init_by_configuration(configuration)

    def init_by_configuration(self, configuration: Dict) -> None:
        if 'mocked_market_name' in configuration:
            self._name = configuration['mocked_market_name']

        mocked_base_currency_balance: Decimal = configuration['mocked_base_currency_balance'] \
            if 'mocked_base_currency_balance' in configuration \
            else DEFAULT_BASE_BALANCE
        assert isinstance(mocked_base_currency_balance, Decimal)

        mocked_base_currency: Decimal = configuration['mocked_base_currency'] \
            if 'mocked_base_currency' in configuration \
            else DEFAULT_BASE_CURRENCY
        self._balances[mocked_base_currency] = mocked_base_currency_balance

        if 'mocked_transaction_maker_fee' in configuration:
            assert isinstance(configuration['mocked_transaction_maker_fee'], Decimal)
            self._transaction_maker_fee = configuration['mocked_transaction_maker_fee']

        if 'mocked_transaction_taker_fee' in configuration:
            assert isinstance(configuration['mocked_transaction_taker_fee'], Decimal)
            self._transaction_taker_fee = configuration['mocked_transaction_taker_fee']

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
                'title': 'Starting balance',
                'description':
                    'Balance for selected pair, that will be available for strategy on the market at beginning.',
                'default': str(DEFAULT_BASE_BALANCE),
                'unit': 'base currency',
            },
            'mocked_transaction_maker_fee': {
                'type': CONFIGURATION_STRUCTURE_TYPE_DECIMAL,
                'title': 'Maker Fee',
                'description':
                    'Transaction fee that will be charged when you add the stock (usually all LIMIT orders).',
                'default': '{0:.4f}'.format(DEFAULT_TRANSACTION_FEE),
                'unit': 'percents',
            },
            'mocked_transaction_taker_fee': {
                'type': CONFIGURATION_STRUCTURE_TYPE_DECIMAL,
                'title': 'Taker Fee',
                'description':
                    'Transaction fee that will be charged when you reduce stock by you action (usually MARKET orders).',
                'default': '{0:.4f}'.format(DEFAULT_TRANSACTION_FEE),
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

    def get_balances(self) -> List[Balance]:
        result = []
        for currency, available_amount in self._balances.items():
            result.append(Balance(self.name, currency, available_amount))

        return result

    def mock_current_price(self, pair: Pair, value: Decimal) -> None:
        self._current_prices[serialize_pair(pair)] = value

    def get_current_price(self, pair: Pair) -> Decimal:
        return self._current_prices[serialize_pair(pair)]

    def place_order(self, order: Order) -> Order:
        fee = self._calculate_fee(order)
        self._initialize_balances(order.pair)

        if order.is_sell():
            self._process_sell(fee, order)
        elif order.is_buy():
            self._process_buy(fee, order)

        order.close(order.created_at)

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

    def _initialize_balances(self, pair: Pair) -> None:
        if pair.base_currency not in self._balances:
            self._balances[pair.base_currency] = Decimal(0)
        if pair.market_currency not in self._balances:
            self._balances[pair.market_currency] = Decimal(0)

    def _process_buy(self, fee: Decimal, order: Order) -> None:
        max_to_buy = round(self.calculate_maximal_amount_to_buy(order.pair, order.rate), 8)
        if max_to_buy < order.quantity:
            raise NotEnoughBalanceToPerformOrderException(
                'Max to buy is {}, you want to buy {}'.format(max_to_buy, order.quantity)
            )
        self._balances[order.pair.base_currency] -= order.quantity * order.rate
        self._balances[order.pair.market_currency] += order.quantity * (1 - fee)

    def _process_sell(self, fee: Decimal, order: Order) -> None:
        max_to_sell = round(self.calculate_maximal_amount_to_sell(order.pair), 8)
        if max_to_sell < order.quantity:
            raise NotEnoughBalanceToPerformOrderException(
                'Max to sell is {}, you want to sell {}'.format(max_to_sell, order.quantity)
            )
        self._balances[order.pair.base_currency] += order.quantity * order.rate * (1 - fee)
        self._balances[order.pair.market_currency] -= order.quantity

    def _calculate_fee(self, order: Order):
        if order.type == ORDER_TYPE_LIMIT:
            return self._transaction_maker_fee

        elif order.type == ORDER_TYPE_MARKET:
            return self._transaction_taker_fee

        raise ValueError('{} is not valid order type'.format(order.type))
