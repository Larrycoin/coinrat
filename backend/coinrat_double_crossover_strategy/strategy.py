import datetime, time
from typing import Union

from coinrat.domain import Strategy, MarketsCandleStorage, Signal, MarketPair

DOUBLE_CROSSOVER_STRATEGY = 'double_crossover'


class DoubleCrossoverStrategy(Strategy):
    """
    @link http://www.financial-spread-betting.com/course/using-two-moving-averages.html
    """

    def __init__(
        self,
        market_name: str,
        pair: MarketPair,
        storage: MarketsCandleStorage,
        long_average_interval: datetime.timedelta,
        short_average_interval: datetime.timedelta,
        delay: int = 30,
        number_of_runs: Union[int, None] = None
    ) -> None:
        assert short_average_interval < long_average_interval

        self._long_average_interval = long_average_interval
        self._short_average_interval = short_average_interval
        self._pair = pair
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._market_name = market_name
        self._storage = storage

    def run(self):
        while self._number_of_runs is None or self._number_of_runs > 0:

            signal = self._check_for_signal()
            if signal is not None:
                self._react_on_signal(signal)

            if self._number_of_runs is not None:
                self._number_of_runs -= 1
            time.sleep(self._delay)

    def _check_for_signal(self) -> Union[Signal, None]:
        now = datetime.datetime.utcnow()
        long_interval = (now - self._long_average_interval, now)
        long_average = self._storage.mean(self._market_name, self._pair, 'closed', long_interval)
        print(long_average)

        short_interval = (now - self._short_average_interval, now)
        short_average = self._storage.mean(self._market_name, self._pair, 'closed', short_interval)
        print(short_average)

    def _react_on_signal(self, signal: Signal):
        pass
