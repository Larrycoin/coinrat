import dateutil
from typing import Dict, List
from bittrex.bittrex import Bittrex, TICKINTERVAL_FIVEMIN, API_V2_0
from decimal import Decimal

from coinrat_market import Balance, Candle


class BittrexMarketRequestException(Exception):
    pass


class BittrexMarket:
    def __init__(self, key: str, secret: str):
        assert key is not None and len(key) > 0
        assert secret is not None and len(secret) > 0

        self.client = Bittrex(key, secret, api_version=API_V2_0)

    def get_balance(self, currency: str):
        result = self.client.get_balance(currency)
        self.validate_result(result)

        return Balance(currency, Decimal(result['result']['Available']))

    def get_candles(self, currency: str) -> List[Candle]:
        result = self.client.get_candles(currency, TICKINTERVAL_FIVEMIN)
        self.validate_result(result)

        for candle in result['result']:
            time = dateutil.parser.parse(candle['T'])

            yield Candle(time, Decimal(candle['L']), Decimal(candle['H']))

    @staticmethod
    def validate_result(result: Dict):
        if not result['success']:
            raise BittrexMarketRequestException(result['message'])
