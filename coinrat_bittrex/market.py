import datetime
import logging
import uuid

import dateutil.parser
from typing import Dict, List
from bittrex.bittrex import Bittrex, API_V1_1, API_V2_0, TICKINTERVAL_ONEMIN
from decimal import Decimal

from coinrat.domain import Market, Balance, Pair, MinuteCandle, Order, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT, \
    PairMarketInfo, MarketPairDoesNotExistsException, NotEnoughBalanceToPerformOrderException


class BittrexMarketRequestException(Exception):
    pass


MARKET_NAME = 'bittrex'


class BittrexMarket(Market):
    def __init__(self, client_v1: Bittrex, client_v2: Bittrex):
        self._client_v1 = client_v1
        self._client_v2 = client_v2

    @property
    def name(self) -> str:
        return MARKET_NAME

    @property
    def transaction_fee_coefficient(self) -> Decimal:
        return Decimal(0.0025)

    def get_balance(self, currency: str):
        currency = self._fix_currency(currency)
        result = self._client_v2.get_balance(currency)
        self._validate_result(result)

        return Balance(self.name, currency, Decimal(result['result']['Available']))

    def get_last_candle(self, pair: Pair) -> MinuteCandle:
        result = self._get_sorted_candles_from_api(pair)
        return self._create_candle_from_raw_ticker_data(pair, result[-1])

    def get_candles(self, pair: Pair) -> List[MinuteCandle]:
        result = self._get_sorted_candles_from_api(pair)
        return [self._create_candle_from_raw_ticker_data(pair, candle_data) for candle_data in result]

    def get_pair_market_info(self, pair: Pair) -> PairMarketInfo:
        market = self.format_market_pair(pair)
        result = self._client_v2.get_markets()
        self._validate_result(result)
        for market_data in result['result']:
            if market_data['MarketName'] == market:
                return PairMarketInfo(pair, Decimal(market_data['MinTradeSize']))

        raise MarketPairDoesNotExistsException(
            'MarketPair "{}" not found on the "{}".'.format(market, self.name)
        )

    def create_sell_order(self, order: Order) -> Order:
        assert order.market_name == self.name

        logging.info('Placing SELL order: {}'.format(order))
        market = self.format_market_pair(order.pair)
        self._validate_minimal_order(order)

        if order.type == ORDER_TYPE_MARKET:
            raise NotImplementedError('Bittrex does not support that.')

        elif order.type == ORDER_TYPE_LIMIT:
            print(market, float(order.quantity), float(order.rate))
            result = self._client_v1.sell_limit(market, float(order.quantity), float(order.rate))
            self._validate_result(result)
            order.set_id_on_market(result['result']['uuid'])
            return order

        else:
            raise ValueError('Unknown order type: {}'.format(order.type))

    def create_buy_order(self, order: Order) -> Order:
        assert order.market_name == self.name

        logging.info('Placing BUY order: {}'.format(order))
        market = self.format_market_pair(order.pair)
        self._validate_minimal_order(order)

        if order.type == ORDER_TYPE_MARKET:
            raise NotImplementedError('Bittrex does not support that.')

        elif order.type == ORDER_TYPE_LIMIT:
            result = self._client_v1.buy_limit(market, float(order.quantity), float(order.rate))
            self._validate_result(result)
            order.set_id_on_market(result['result']['uuid'])
            return order

        else:
            raise ValueError('Unknown order type: {}'.format(order.type))

    def cancel_order(self, order_id: str) -> None:
        result = self._client_v1.cancel(order_id)
        self._validate_result(result)

    def buy_max_available(self, pair: Pair) -> Order:
        base_currency_balance = self.get_balance(pair.base_currency)
        tick = self.get_last_candle(pair)

        coefficient_due_fee = Decimal(1) - self.transaction_fee_coefficient
        amount_to_buy = (base_currency_balance.available_amount / tick.average_price) * coefficient_due_fee
        order = Order(uuid.uuid4(), self.name, pair, ORDER_TYPE_LIMIT, amount_to_buy, tick.average_price)
        return self.create_buy_order(order)

    def _validate_minimal_order(self, order: Order) -> None:
        pair_market_info = self.get_pair_market_info(order.pair)
        if pair_market_info.minimal_order_size > order.quantity:
            raise NotEnoughBalanceToPerformOrderException(
                'You want {} but limit is {}.'.format(order.quantity, pair_market_info.minimal_order_size)
            )

    def sell_max_available(self, pair: Pair) -> Order:
        market_currency_available = self.get_balance(pair.market_currency).available_amount
        tick = self.get_last_candle(pair)
        order = Order(uuid.uuid4(), self.name, pair, ORDER_TYPE_LIMIT, market_currency_available, tick.average_price)
        return self.create_sell_order(order)

    def _get_sorted_candles_from_api(self, pair: Pair):
        market = self.format_market_pair(pair)
        result = self._client_v2.get_candles(market, TICKINTERVAL_ONEMIN)
        self._validate_result(result)
        result = result['result']
        result.sort(key=lambda candle: candle['T'])
        return result

    def _create_candle_from_raw_ticker_data(self, pair: Pair, candle: Dict[str, str]) -> MinuteCandle:
        return MinuteCandle(
            self.name,
            pair,
            dateutil.parser.parse(candle['T']).replace(tzinfo=datetime.timezone.utc),
            Decimal(candle['O']),
            Decimal(candle['H']),
            Decimal(candle['L']),
            Decimal(candle['C'])
        )

    @staticmethod
    def format_market_pair(pair: Pair):
        return '{}-{}'.format(
            BittrexMarket._fix_currency(pair.base_currency),
            BittrexMarket._fix_currency(pair.market_currency)
        )

    @staticmethod
    def _validate_result(result: Dict):
        if not result['success']:
            raise BittrexMarketRequestException(result['message'])

    @staticmethod
    def _fix_currency(currency):
        return 'USDT' if currency == 'USD' else currency


def bittrex_market_factory(key: str, secret: str) -> BittrexMarket:
    return BittrexMarket(Bittrex(key, secret, api_version=API_V1_1), Bittrex(key, secret, api_version=API_V2_0))
