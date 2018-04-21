import time, logging
from datetime import datetime, timezone
from typing import Dict, List, Union
from decimal import Decimal

from requests import Session, RequestException, TooManyRedirects
from coinrat.domain import MarketStateSynchronizer
from coinrat.domain.candle import Candle, CandleStorage
from coinrat.domain.pair import Pair
from coinrat.event.event_emitter import EventEmitter

SYNCHRONIZER_NAME = 'cryptocompare'

MINUTE_CANDLE_URL = 'https://min-api.cryptocompare.com/data/histominute?fsym={}&tsym={}&limit=1&aggregate=1&e={}'
ALL_EXCHANGES_URL = 'https://min-api.cryptocompare.com/data/all/exchanges'

MARKET_MAP = {
    'bittrex': 'BitTrex'
}


class CryptocompareRequestException(Exception):
    pass


class CryptocompareSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        storage: CandleStorage,
        event_emitter: EventEmitter,
        session: Session,
        delay: int = 30,
        number_of_runs: Union[int, None] = None,
        time_to_sleep_after_error: int = 10,
        max_number_of_retries: Union[int, None] = None
    ) -> None:
        self._storage = storage
        self._event_emitter = event_emitter
        self._session = session
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._time_to_sleep_after_error = time_to_sleep_after_error
        self._default_max_number_of_retries = max_number_of_retries
        self._max_number_of_retries = max_number_of_retries

    def synchronize(self, market_name: str, pair: Pair) -> None:
        markets = self._get_all_exchanges()
        if market_name not in markets:
            raise ValueError('Market "{}" not supported by Cryptocompare.'.format(market_name))
        cryptocompare_exchange_name = markets[market_name]

        while self._number_of_runs is None or self._number_of_runs > 0:
            url = MINUTE_CANDLE_URL.format(pair.market_currency, pair.base_currency, cryptocompare_exchange_name)

            data = self.get_data_from_cryptocompare(url)

            candles_data: List[Dict] = data['Data']
            candles = [self._create_candle_from_raw(market_name, pair, candle) for candle in candles_data]
            self._storage.write_candles(candles)
            self._event_emitter.emit_new_candles(self._storage.name, candles)

            if self._number_of_runs is not None:  # pragma: no cover
                self._number_of_runs -= 1

            time.sleep(self._delay)

    def get_supported_markets(self) -> List[str]:
        return self._get_all_exchanges().keys()

    def _get_all_exchanges(self) -> Dict[str, str]:
        response = self._session.get(ALL_EXCHANGES_URL)
        data: Dict = response.json()

        result = {}
        for key, items in data.items():
            result[key.lower()] = key

        return result

    def get_data_from_cryptocompare(self, url: str) -> Dict:
        while True:
            try:
                response = self._session.get(url)
                if response.status_code != 200:
                    raise CryptocompareRequestException(response.text)

                json_data = response.json()
                if json_data['Response'] != 'Success':
                    raise CryptocompareRequestException(response.text)

                self._reset_number_of_retries()

                return json_data
            except TooManyRedirects as e:
                raise e
            except (RequestException, CryptocompareRequestException) as e:
                if not self._should_suppress_connection_exception_and_retry():
                    raise e

                logging.error('Error in connection to "{}", error: "{}".'.format(url, str(e)))
                time.sleep(self._time_to_sleep_after_error)
                self._count_connection_error_retry()

    @staticmethod
    def _create_candle_from_raw(market_name: str, pair: Pair, candles_data: Dict) -> Candle:
        return Candle(
            market_name,
            pair,
            datetime.fromtimestamp(candles_data['time']).astimezone(timezone.utc),
            Decimal(candles_data['open']),
            Decimal(candles_data['high']),
            Decimal(candles_data['low']),
            Decimal(candles_data['close'])
        )

    def _count_connection_error_retry(self):
        if self._max_number_of_retries is not None:
            self._max_number_of_retries -= 1

    def _should_suppress_connection_exception_and_retry(self) -> bool:
        return self._max_number_of_retries is None or self._max_number_of_retries > 0

    def _reset_number_of_retries(self) -> None:
        self._max_number_of_retries = self._default_max_number_of_retries
