import datetime, time
import logging
from typing import Union, Tuple, List
from decimal import Decimal

import math

from coinrat.domain import Strategy, CandleStorage, Order, OrderStorage, Pair, CANDLE_STORAGE_FIELD_CLOSE, Market, \
    DIRECTION_SELL, DIRECTION_BUY, ORDER_STATUS_OPEN, MarketOrderException, \
    StrategyConfigurationException, NotEnoughBalanceToPerformOrderException
from coinrat_double_crossover_strategy.signal import Signal, SIGNAL_BUY, SIGNAL_SELL
from coinrat_double_crossover_strategy.utils import absolute_possible_percentage_gain

STRATEGY_NAME = 'double_crossover'


class DoubleCrossoverStrategy(Strategy):
    """
    @link http://www.financial-spread-betting.com/course/using-two-moving-averages.html
    """

    def __init__(
        self,
        pair: Pair,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        long_average_interval: datetime.timedelta,
        short_average_interval: datetime.timedelta,
        delay: int = 30,
        number_of_runs: Union[int, None] = None
    ) -> None:
        assert short_average_interval < long_average_interval

        self._pair = pair
        self._candle_storage = candle_storage
        self._order_storage = order_storage
        self._long_average_interval = long_average_interval
        self._short_average_interval = short_average_interval
        self._delay = delay
        self._number_of_runs = number_of_runs
        self._previous_sign = None
        self._strategy_ticker = 0
        self._last_signal: Union[Signal, None] = None

    def run(self, markets: List[Market]) -> None:
        if len(markets) != 1:
            message = 'This strategy works only with one market, {} given.'.format(len(markets))
            raise StrategyConfigurationException(message)

        market = markets[0]

        while self._number_of_runs is None or self._number_of_runs > 0:
            self._check_and_process_open_orders(market)
            self._check_for_signal_and_trade(market)

            if self._number_of_runs is not None:  # pragma: no cover
                self._number_of_runs -= 1

            self._strategy_ticker += 1
            time.sleep(self._delay)

    def _check_and_process_open_orders(self, market: Market):
        orders = self._order_storage.find_by(market_name=market.name, pair=self._pair, status=ORDER_STATUS_OPEN)
        for order in orders:
            status = market.get_order_status(order)
            if status.is_open is False:
                order.close(status.closed_at)
                self._order_storage.save_order(order)
                logging.info('Order "{}" has been successfully CLOSED.'.format(order.order_id))

    def _check_for_signal_and_trade(self, market: Market):
        signal = self._check_for_signal(market)
        if signal is not None:
            self._last_signal = signal

        if self._last_signal is not None:
            order = self._trade_on_signal(market)
            if order is not None:
                self._order_storage.save_order(order)

    def _does_trade_worth_it(self, market: Market) -> bool:
        last_order = self._order_storage.find_last_order(market.name, self._pair)
        if last_order is None:
            return True

        current_price = self._candle_storage.get_current_candle(market.name, self._pair).average_price

        does_worth_it = absolute_possible_percentage_gain(last_order.rate, current_price) > market.transaction_fee
        if not does_worth_it:
            logging.info('Skipping trade at current price: "{0:.8f}" (last order at: "{1:.8f}")'.format(
                current_price, last_order.rate
            ))

        return does_worth_it

    def _check_for_signal(self, market: Market) -> Union[Signal, None]:
        long_average, short_average = self._get_averages(market)
        current_sign = self._calculate_sign_of_change(long_average, short_average)

        logging.info(
            '[{0}] Previous_sign: {1}, Current-sign: {2:.8f}, Long-now: {3:.8f}, Short-now: {4:.8f}'.format(
                self._strategy_ticker,
                self._previous_sign,
                current_sign,
                long_average,
                short_average
            )
        )

        if current_sign == 0:  # In equal situation, we are waiting for next price movement to decide
            return None

        signal = None
        if self._previous_sign is not None and current_sign != self._previous_sign:
            signal = self._create_signal(current_sign)

        self._previous_sign = current_sign
        return signal

    @staticmethod
    def _create_signal(current_sign: int) -> Signal:
        assert current_sign in [-1, 1]
        if current_sign == 1:
            return Signal(SIGNAL_BUY)
        return Signal(SIGNAL_SELL)

    @staticmethod
    def _calculate_sign_of_change(long_average: Decimal, short_average: Decimal) -> int:
        diff = short_average - long_average
        if diff == 0:
            return 0

        return int(math.copysign(1, diff))

    def _get_averages(self, market: Market) -> Tuple[Decimal, Decimal]:
        now = datetime.datetime.now().astimezone(datetime.timezone.utc)  # Todo: DateTimeFactory
        long_interval = (now - self._long_average_interval, now)
        long_average = self._candle_storage.mean(
            market.name,
            self._pair,
            CANDLE_STORAGE_FIELD_CLOSE,
            long_interval
        )
        short_interval = (now - self._short_average_interval, now)
        short_average = self._candle_storage.mean(
            market.name,
            self._pair,
            CANDLE_STORAGE_FIELD_CLOSE,
            short_interval
        )

        return long_average, short_average

    def _trade_on_signal(self, market: Market) -> Union[Order, None]:
        order = None
        logging.info('Checking trade on signal: "{}".'.format(self._last_signal))
        try:
            if self._last_signal.is_buy():
                self._cancel_open_order(market, DIRECTION_SELL)
                if self._does_trade_worth_it(market):
                    order = market.buy_max_available(self._pair)
                    self._last_signal = None

            elif self._last_signal.is_sell():
                self._cancel_open_order(market, DIRECTION_BUY)
                if self._does_trade_worth_it(market):
                    order = market.sell_max_available(self._pair)
                    self._last_signal = None
            else:
                raise ValueError('Unknown signal: "{}"'.format(self._last_signal))  # pragma: no cover

        except NotEnoughBalanceToPerformOrderException as e:
            # Intentionally, this strategy does not need state of order,
            # just ignores buy/sell and waits for next signal.
            logging.warning(e)

        return order

    def _cancel_open_order(self, market: Market, direction: str):
        orders = self._order_storage.find_by(
            market_name=market.name,
            pair=self._pair,
            status=ORDER_STATUS_OPEN,
            direction=direction
        )
        for order in orders:
            try:
                market.cancel_order(order.id_on_market)
            except MarketOrderException as e:
                logging.error('Order "{}" cancelling failed: Error: "{}"!'.format(order.order_id, e))
                return

            order.cancel(datetime.datetime.now().astimezone(datetime.timezone.utc))
            self._order_storage.save_order(order)
            logging.info('Order "{}" has been CANCELED!'.format(order.order_id))
