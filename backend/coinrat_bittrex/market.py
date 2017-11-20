import datetime
from typing import Dict
from bittrex.bittrex import Bittrex, API_V1_1, API_V2_0, ORDERTYPE_LIMIT, ORDERTYPE_MARKET, TICKINTERVAL_ONEMIN
from decimal import Decimal
from coinrat_market import Balance, Candle, Order, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, MarketPair, Market


class BittrexMarketRequestException(Exception):
    pass


class BittrexMarket(Market):
    def __init__(self, key: str, secret: str):
        assert key is not None and len(key) > 0
        assert secret is not None and len(secret) > 0

        self._client_v1 = Bittrex(key, secret, api_version=API_V1_1)
        self._client_v2 = Bittrex(key, secret, api_version=API_V2_0)

    @property
    def transaction_fee_coefficient(self):
        return 0.0025

    def get_balance(self, currency: str):
        result = self._client_v2.get_balance(currency)
        self._validate_result(result)

        return Balance(currency, Decimal(result['result']['Available']))

    def get_last_ticker(self, currency: str) -> Candle:
        result = self._client_v1.get_ticker(currency)
        self._validate_result(result)

        return Candle(datetime.datetime.now(), Decimal(result['result']['Bid']), Decimal(result['result']['Ask']))

    def create_sell_order(self, order: Order) -> str:
        market = self.format_market_pair(order.pair)

        if order.type == ORDER_TYPE_MARKET:
            raise Exception('Not implemented')  # Todo: implement

        elif order.type == ORDER_TYPE_LIMIT:
            result = self._client_v1.sell_limit(market, order.quantity, order.rate)
            self._validate_result(result)
            return result['result']['uuid']

        else:
            raise ValueError('Unknown order type: {}'.format(order.type))

    def create_buy_order(self, order: Order) -> str:
        market = self.format_market_pair(order.pair)

        if order.type == ORDER_TYPE_MARKET:
            raise Exception('Not implemented')  # Todo: implement

        elif order.type == ORDER_TYPE_LIMIT:
            result = self._client_v1.buy_limit(market, order.quantity, order.rate)
            self._validate_result(result)
            return result['result']['uuid']

        else:
            raise ValueError('Unknown order type: {}'.format(order.type))

    def cancel_order(self, order_id: str) -> None:
        result = self._client_v1.cancel(id)
        self._validate_result(result)

    def buy_max_available(self, pair: MarketPair) -> str:
        balance = self.get_balance(pair.left)
        market = self.format_market_pair(pair)
        tick = self.get_last_ticker(market)
        can_buy = (balance.available_amount / tick.average_price) * Decimal(1 - self.transaction_fee_coefficient)
        return self.create_buy_order(Order(pair, ORDER_TYPE_LIMIT, can_buy, tick.average_price))

    def sell_max_available(self, pair: MarketPair) -> str:
        balance = self.get_balance(pair.right)
        market = self.format_market_pair(pair)
        tick = self.get_last_ticker(market)
        can_sell = (tick.average_price * balance.available_amount) * Decimal(1 - self.transaction_fee_coefficient)
        return self.create_buy_order(Order(pair, ORDER_TYPE_LIMIT, can_sell, tick.average_price))

    @staticmethod
    def format_market_pair(pair: MarketPair):
        return '{}-{}'.format(pair.left, pair.right)

    @staticmethod
    def _validate_result(result: Dict):
        if not result['success']:
            raise BittrexMarketRequestException(result['message'])

    @staticmethod
    def _map_order_type_to_bittrex(order_type: str):
        return {ORDER_TYPE_LIMIT: ORDERTYPE_LIMIT, ORDER_TYPE_MARKET: ORDERTYPE_MARKET}[order_type]


def bittrex_market_factory(key: str, secret: str) -> BittrexMarket:
    return BittrexMarket(Bittrex(key, secret, api_version=API_V1_1), Bittrex(key, secret, api_version=API_V2_0))
