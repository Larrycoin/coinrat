import dateutil.parser
from typing import Dict, List
from bittrex.bittrex import Bittrex, TICKINTERVAL_FIVEMIN, API_V1_1, API_V2_0, ORDERTYPE_LIMIT, ORDERTYPE_MARKET
from decimal import Decimal

from coinrat_market import Balance, Candle, Order, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, MarketPair


class BittrexMarketRequestException(Exception):
    pass


class BittrexMarket:
    def __init__(self, key: str, secret: str):
        assert key is not None and len(key) > 0
        assert secret is not None and len(secret) > 0

        self._client_v1 = Bittrex(key, secret, api_version=API_V1_1)
        self._client_v2 = Bittrex(key, secret, api_version=API_V2_0)

    def get_balance(self, currency: str):
        result = self._client_v2.get_balance(currency)
        self._validate_result(result)

        return Balance(currency, Decimal(result['result']['Available']))

    def get_candles(self, currency: str) -> List[Candle]:
        result = self._client_v2.get_candles(currency, TICKINTERVAL_FIVEMIN)
        self._validate_result(result)

        for candle in result['result']:
            time = dateutil.parser.parse(candle['T'])

            yield Candle(time, Decimal(candle['L']), Decimal(candle['H']))

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

    def cancel_order(self, id: str) -> None:
        result = self._client_v1.cancel(id)
        self._validate_result(result)
        print(result)

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
