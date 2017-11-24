import datetime, time
import logging
from typing import Union, Tuple, List
from decimal import Decimal

import math

from coinrat.domain import Strategy, MarketsCandleStorage, Signal, MarketPair, \
    CANDLE_STORAGE_FIELD_CLOSE, SIGNAL_SELL, SIGNAL_BUY, Market, \
    StrategyConfigurationException, NotEnoughBalanceToPerformOrderException

STRATEGY_NAME = 'double_crossover'


class DoubleCrossoverStrategy(Strategy):
    """
    @link http://www.financial-spread-betting.com/course/using-two-moving-averages.html
    """

    def __init__(
        self,
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
        self._storage = storage
        self._previous_sign = None
        self._strategy_ticker = 0

    def run(self, markets: List[Market]) -> None:
        if len(markets) != 1:
            message = 'This strategy works only with one market, {} given.'.format(len(markets))
            raise StrategyConfigurationException(message)

        market = markets[0]

        while self._number_of_runs is None or self._number_of_runs > 0:

            signal = self._check_for_signal(market)
            if signal is not None:
                self._react_on_signal(market, signal)

            if self._number_of_runs is not None:
                self._number_of_runs -= 1

            self._strategy_ticker += 1
            time.sleep(self._delay)

    def _check_for_signal(self, market: Market) -> Union[Signal, None]:
        long_average, short_average = self._get_averages(market)
        current_sign = math.copysign(1, short_average - long_average)

        logging.debug(
            '[{}] Previous_sign: {}, Current-sign: {}, Long-now: {}, Short-now: {}'.format(
                self._strategy_ticker,
                self._previous_sign,
                current_sign,
                long_average,
                short_average
            )
        )

        signal = None
        if self._previous_sign is not None and current_sign != self._previous_sign:
            if current_sign == 1:
                signal = Signal(SIGNAL_BUY)
            elif current_sign == -1:
                signal = Signal(SIGNAL_SELL)

        self._previous_sign = current_sign
        return signal

    def _get_averages(self, market: Market) -> Tuple[Decimal, Decimal]:
        now = datetime.datetime.now().astimezone(datetime.timezone.utc)  # Todo: DateTimeFactory
        long_interval = (now - self._long_average_interval, now)
        long_average = self._storage.mean(
            market.get_name(),
            self._pair,
            CANDLE_STORAGE_FIELD_CLOSE,
            long_interval
        )
        short_interval = (now - self._short_average_interval, now)
        short_average = self._storage.mean(
            market.get_name(),
            self._pair,
            CANDLE_STORAGE_FIELD_CLOSE,
            short_interval
        )

        return long_average, short_average

    def _react_on_signal(self, market: Market, signal: Signal):
        try:
            if signal.is_buy():
                market.buy_max_available(self._pair)
            elif signal.is_sell():
                market.sell_max_available(self._pair)
            else:
                raise ValueError('Unknown signal: "{}"'.format(signal))

        except NotEnoughBalanceToPerformOrderException as e:
            # Intentionally, this strategy does not need state od order,
            # just ignores buy/sell and waits for next signal.
            logging.warning(e)
