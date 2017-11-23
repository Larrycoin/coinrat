import datetime
import logging
import dateutil.parser
from typing import Dict, List
from bittrex.bittrex import Bittrex, API_V1_1, API_V2_0, ORDERTYPE_LIMIT, ORDERTYPE_MARKET, TICKINTERVAL_ONEMIN
from decimal import Decimal

from coinrat.domain import Market, Balance, MarketPair, MinuteCandle, Order, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, \
    PairMarketInfo, MarketPairDoesNotExistsException


class BittrexMarketRequestException(Exception):
    pass


MARKET_NAME = 'bittrex'


class BittrexMarket(Market):
    def __init__(self, client_v1: Bittrex, client_v2: Bittrex, market_name: str = 'bittrex'):
        self._client_v1 = client_v1
        self._client_v2 = client_v2
        self._market_name = market_name

    def get_name(self) -> str:
        return MARKET_NAME

    @property
    def transaction_fee_coefficient(self) -> Decimal:
        return Decimal(0.0025)

    def get_balance(self, currency: str):
        currency = self._fix_currency(currency)
        result = self._client_v2.get_balance(currency)
        self._validate_result(result)

        return Balance(self._market_name, currency, Decimal(result['result']['Available']))

    def get_last_candle(self, pair: MarketPair) -> MinuteCandle:
        result = self._get_sorted_candles_from_api(pair)
        return self._create_candle_from_raw_ticker_data(pair, result[-1])

    def get_candles(self, pair: MarketPair) -> List[MinuteCandle]:
        result = self._get_sorted_candles_from_api(pair)
        return [self._create_candle_from_raw_ticker_data(pair, candle_data) for candle_data in result]

    def get_pair_market_info(self, pair: MarketPair) -> PairMarketInfo:
        market = self.format_market_pair(pair)
        result = self._client_v2.get_markets()
        self._validate_result(result)
        for market_data in result['result']:
            if market_data['MarketName'] == market:
                return PairMarketInfo(pair, Decimal(market_data['MinTradeSize']))

        raise MarketPairDoesNotExistsException(
            'MarketPair "{}" not found on the "{}".'.format(market, self._market_name)
        )

    def create_sell_order(self, order: Order) -> str:
        logging.info('Placing SELL order: {}'.format(order))
        market = self.format_market_pair(order.pair)

        if order.type == ORDER_TYPE_MARKET:
            raise NotImplementedError('Not implemented')  # Todo: implement

        elif order.type == ORDER_TYPE_LIMIT:
            result = self._client_v1.sell_limit(market, float(order.quantity), float(order.rate))
            self._validate_result(result)
            return result['result']['uuid']

        else:
            raise ValueError('Unknown order type: {}'.format(order.type))

    def create_buy_order(self, order: Order) -> str:
        logging.info('Placing BUY order: {}'.format(order))
        market = self.format_market_pair(order.pair)

        if order.type == ORDER_TYPE_MARKET:
            raise Exception('Not implemented')  # Todo: implement

        elif order.type == ORDER_TYPE_LIMIT:
            result = self._client_v1.buy_limit(market, float(order.quantity), float(order.rate))
            self._validate_result(result)
            return result['result']['uuid']

        else:
            raise ValueError('Unknown order type: {}'.format(order.type))

    def cancel_order(self, order_id: str) -> None:
        result = self._client_v1.cancel(order_id)
        self._validate_result(result)

    def buy_max_available(self, pair: MarketPair) -> str:
        balance = self.get_balance(pair.base_currency)
        tick = self.get_last_candle(pair)
        can_buy = (balance.available_amount / tick.average_price) * Decimal(1 - self.transaction_fee_coefficient)
        return self.create_buy_order(Order(pair, ORDER_TYPE_LIMIT, can_buy, tick.average_price))

    def sell_max_available(self, pair: MarketPair) -> str:
        balance = self.get_balance(pair.market_currency)
        tick = self.get_last_candle(pair)
        return self.create_sell_order(Order(pair, ORDER_TYPE_LIMIT, balance.available_amount, tick.average_price))

    def _get_sorted_candles_from_api(self, pair: MarketPair):
        market = self.format_market_pair(pair)
        result = self._client_v2.get_candles(market, TICKINTERVAL_ONEMIN)
        self._validate_result(result)
        result = result['result']
        result.sort(key=lambda candle: candle['T'])
        return result

    def _create_candle_from_raw_ticker_data(self, pair: MarketPair, candle: Dict[str, str]) -> MinuteCandle:
        return MinuteCandle(
            self._market_name,
            pair,
            dateutil.parser.parse(candle['T']).replace(tzinfo=datetime.timezone.utc),
            Decimal(candle['O']),
            Decimal(candle['C']),
            Decimal(candle['L']),
            Decimal(candle['H']),
        )

    @staticmethod
    def format_market_pair(pair: MarketPair):
        return '{}-{}'.format(
            BittrexMarket._fix_currency(pair.base_currency),
            BittrexMarket._fix_currency(pair.market_currency)
        )

    @staticmethod
    def _validate_result(result: Dict):
        if not result['success']:
            raise BittrexMarketRequestException(result['message'])

    @staticmethod
    def _map_order_type_to_bittrex(order_type: str):
        return {ORDER_TYPE_LIMIT: ORDERTYPE_LIMIT, ORDER_TYPE_MARKET: ORDERTYPE_MARKET}[order_type]

    @staticmethod
    def _fix_currency(currency):
        return 'USDT' if currency == 'USD' else currency


def bittrex_market_factory(key: str, secret: str) -> BittrexMarket:
    return BittrexMarket(Bittrex(key, secret, api_version=API_V1_1), Bittrex(key, secret, api_version=API_V2_0))
