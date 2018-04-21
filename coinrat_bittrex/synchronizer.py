import logging
import time
import traceback
from typing import Union, List

from coinrat.domain import MarketStateSynchronizer
from coinrat.domain.candle import CandleStorage
from coinrat.domain.market import MarketException
from coinrat.domain.pair import Pair
from coinrat.event.event_emitter import EventEmitter
from .market import BittrexMarket, MARKET_NAME

logger = logging.getLogger(__name__)


class BittrexSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        market: BittrexMarket,
        storage: CandleStorage,
        event_emitter: EventEmitter,
        delay: int = 60,
        number_of_runs: Union[int, None] = None
    ) -> None:
        self._market = market
        self._storage = storage
        self._event_emitter = event_emitter
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._needs_resync_of_historical_data = True

    def synchronize(self, market_name: str, pair: Pair):
        if market_name != MARKET_NAME:
            raise ValueError('BittrexSynchronizer does not support market "{}".'.format(market_name))

        while self._number_of_runs is None or self._number_of_runs > 0:

            try:
                if self._needs_resync_of_historical_data:
                    logger.info('Resync of all available history (on start / after error)')
                    candles = self._market.get_candles(pair)
                    self._storage.write_candles(candles)

                else:
                    candles = self._market.get_last_minute_candles(pair, 3)
                    self._storage.write_candles(candles)
                    self._event_emitter.emit_new_candles(self._storage.name, candles)

                self._needs_resync_of_historical_data = False

            except MarketException as e:
                message = 'Loading data from market failed (next try in: {} seconds): {}'.format(self._delay, str(e))
                traceback.print_exc()
                logger.warning(message)
                self._needs_resync_of_historical_data = True

            if self._number_of_runs is not None:  # pragma: no cover
                self._number_of_runs -= 1

            time.sleep(self._delay)

    def get_supported_markets(self) -> List[str]:
        return [MARKET_NAME]
