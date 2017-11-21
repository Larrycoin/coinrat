import time
from datetime import datetime
from typing import Dict, List

from decimal import Decimal
from requests import Session

from coinrat.market import MarketStateSynchronizer, MarketStorage, MarketPair, MinuteCandle

MINUTE_CANDLE_URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&limit=1&aggregate=1&e={}'
MARKET_MAP = {
    'bittrex': 'BitTrex'
}


class CryptocompareRequestException(Exception):
    pass


class CryptocompareSynchronizer(MarketStateSynchronizer):
    def __init__(self, market_name: str, storage: MarketStorage, session: Session) -> None:
        self._market_name = market_name
        self._storage = storage
        self._session = session

    def synchronize(self, pair: MarketPair) -> None:
        while True:
            url = MINUTE_CANDLE_URL.format(pair.right, pair.left, MARKET_MAP[self._market_name])
            data = self.get_data_from_cryptocompare(url)
            candles_data: List[Dict] = data['Data']
            self._storage.write_candles(self._market_name, list(map(self._create_candle_from_raw, candles_data)))
            time.sleep(30)

    def get_data_from_cryptocompare(self, url: str) -> Dict:
        response = self._session.get(url)
        if response.status_code != 200:
            raise CryptocompareRequestException(response.text())

        response = response.json()
        if response['Response'] != 'Success':
            raise CryptocompareRequestException(response.text())

        return response

    def _create_candle_from_raw(self, candles_data: Dict) -> MinuteCandle:
        """
        {'time': 1511287560, 'close': 8303, 'high': 8303, 'low': 8301, 'open': 8301, 'volumefrom': 1.22, 'volumeto': 10109.63}
        """
        return MinuteCandle(
            datetime.fromtimestamp(candles_data['time']),
            Decimal(candles_data['open']),
            Decimal(candles_data['close']),
            Decimal(candles_data['low']),
            Decimal(candles_data['high'])
        )
