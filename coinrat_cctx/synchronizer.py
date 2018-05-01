import ccxt
import logging

from typing import Union, List

from coinrat.domain import MarketStateSynchronizer
from coinrat.domain.candle import CandleStorage
from coinrat.domain.pair import Pair
from coinrat.event.event_emitter import EventEmitter

logger = logging.getLogger(__name__)


class CctxSynchronizer(MarketStateSynchronizer):
    def __init__(
        self,
        storage: CandleStorage,
        event_emitter: EventEmitter,
        delay: int = 30,
        number_of_runs: Union[int, None] = None,
    ) -> None:
        self._storage = storage
        self._event_emitter = event_emitter
        self._delay = delay
        self._number_of_runs = number_of_runs

    def synchronize(self, market_name: str, pair: Pair):
        pass

    def get_supported_markets(self) -> List[str]:
        return ccxt.exchanges
