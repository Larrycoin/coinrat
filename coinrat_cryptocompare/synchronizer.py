import time, logging
from datetime import datetime, timezone
from typing import Dict, List, Union

from decimal import Decimal

import requests
from requests import Session, RequestException, TooManyRedirects

from coinrat.domain import MarketStateSynchronizer, CandleStorage, Pair, MinuteCandle

MINUTE_CANDLE_URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&limit=1&aggregate=1&e={}'
MARKET_MAP = {
    'bittrex': 'BitTrex'
}


class CryptocompareRequestException(Exception):
    pass


SYNCHRONIZER_NAME = 'cryptocompare'


class CryptocompareSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        market_name: str,
        storage: CandleStorage,
        session: Session,
        delay: int = 30,
        number_of_runs: Union[int, None] = None
    ) -> None:
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._market_name = market_name
        self._storage = storage
        self._session = session

    def synchronize(self, pair: Pair) -> None:
        while self._number_of_runs is None or self._number_of_runs > 0:
            url = MINUTE_CANDLE_URL.format(pair.market_currency, pair.base_currency, MARKET_MAP[self._market_name])

            data = self.get_data_from_cryptocompare(url)

            candles_data: List[Dict] = data['Data']
            candles = [self._create_candle_from_raw(pair, candle) for candle in candles_data]
            self._storage.write_candles(candles)

            if self._number_of_runs is not None:  # pragma: no cover
                self._number_of_runs -= 1

            time.sleep(self._delay)

    def get_data_from_cryptocompare(self, url: str) -> Dict:
        while True:
            try:
                response = self._session.get(url)
                break
            except TooManyRedirects as e:
                raise e
            except RequestException as e:
                logging.error('Error in connection to "{url}", error: {}', e)

            time.sleep(30)

        if response.status_code != 200:
            raise CryptocompareRequestException(response.text())

        json_data = response.json()
        if json_data['Response'] != 'Success':
            raise CryptocompareRequestException(response.text())

        return json_data

    def _create_candle_from_raw(self, pair: Pair, candles_data: Dict) -> MinuteCandle:
        return MinuteCandle(
            self._market_name,
            pair,
            datetime.fromtimestamp(candles_data['time']).astimezone(timezone.utc),
            Decimal(candles_data['open']),
            Decimal(candles_data['high']),
            Decimal(candles_data['low']),
            Decimal(candles_data['close'])
        )
