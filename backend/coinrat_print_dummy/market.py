from decimal import Decimal

from coinrat.domain import Market, Balance, MarketPair, Order

MARKET_NAME = 'print_mockup'
DUMMY_STATIC_BALANCE = Decimal(0.5)
DUMMY_ORDER_ID = 'aaaa-bbbb-cccc-dddd'


class PrintDummyMarket(Market):
    def get_name(self) -> str:
        return MARKET_NAME

    @property
    def transaction_fee_coefficient(self) -> Decimal:
        return Decimal(0.0025)

    def get_balance(self, currency: str):
        return Balance(MARKET_NAME, currency, DUMMY_STATIC_BALANCE)

    def create_sell_order(self, order: Order) -> str:
        print('Creating SELL order {}'.format(order))
        return DUMMY_ORDER_ID

    def create_buy_order(self, order: Order) -> str:
        print('Creating BUY order {}'.format(order))
        return DUMMY_ORDER_ID

    def cancel_order(self, order_id: str) -> None:
        print('Cancelling order #{}'.format(order_id))
        pass

    def buy_max_available(self, pair: MarketPair) -> str:
        print('BUYING max available for: {}'.format(pair))
        return DUMMY_ORDER_ID

    def sell_max_available(self, pair: MarketPair) -> str:
        print('SELLING max available for: {}'.format(pair))
        return DUMMY_ORDER_ID
