import datetime
import logging
import uuid
from typing import Union, Tuple, List, Dict
from decimal import Decimal

import math

from coinrat.domain.market import Market, MarketException
from coinrat.domain import DateTimeFactory, DateTimeInterval
from coinrat.domain.strategy import Strategy, StrategyConfigurationException, StrategyRun, SkipTickException
from coinrat.domain.candle import CandleStorage, CANDLE_STORAGE_FIELD_CLOSE, NoCandlesForMarketInStorageException
from coinrat.domain.order import Order, OrderStorage, DIRECTION_SELL, DIRECTION_BUY, ORDER_STATUS_OPEN, \
    NotEnoughBalanceToPerformOrderException, ORDER_TYPE_LIMIT
from coinrat_double_crossover_strategy.signal import Signal, SIGNAL_BUY, SIGNAL_SELL
from coinrat_double_crossover_strategy.utils import absolute_possible_percentage_gain
from coinrat.event.event_emitter import EventEmitter
from coinrat.domain.configuration_structure import CONFIGURATION_STRUCTURE_TYPE_INT
from coinrat.domain.configuration_structure import format_data_to_python_types

logger = logging.getLogger(__name__)

STRATEGY_NAME = 'double_crossover'

DEFAULT_LONG_AVERAGE = 60 * 60
DEFAULT_SHORT_AVERAGE = 60 * 15


class DoubleCrossoverStrategy(Strategy):
    """
    @link http://www.financial-spread-betting.com/course/using-two-moving-averages.html

    Configuration example:

        {
            'long_average_interval': 60 * 60,  # number of seconds for "long" moving average
            'short_average_interval': 15 * 60,  # number of seconds for "short" moving average
            'delay': 0,  # number of seconds between checks,
            'number_of_runs': None,  # How many checks before termination. None for infinite lop. (Mostly for testing.)
        }

    """

    def __init__(
        self,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        event_emitter: EventEmitter,
        datetime_factory: DateTimeFactory,
        strategy_run: StrategyRun
    ) -> None:
        self._candle_storage = candle_storage
        self._order_storage = order_storage
        self._event_emitter = event_emitter
        self._datetime_factory = datetime_factory
        self._strategy_run = strategy_run

        self._previous_sign: Union[int, None] = None
        self._strategy_ticker = 0
        self._last_signal: Union[Signal, None] = None

        self._long_average_interval = datetime.timedelta(seconds=DEFAULT_LONG_AVERAGE)
        self._short_average_interval = datetime.timedelta(seconds=DEFAULT_SHORT_AVERAGE)
        self._delay = 30
        self._process_configuration(strategy_run.strategy_configuration)

    def _process_configuration(self, strategy_configuration: Dict) -> None:
        configuration = format_data_to_python_types(strategy_configuration, self.get_configuration_structure())

        long_average_interval = datetime.timedelta(minutes=60)
        if 'long_average_interval' in configuration:
            long_average_interval = datetime.timedelta(seconds=int(configuration['long_average_interval']))

        short_average_interval = datetime.timedelta(minutes=15)
        if 'short_average_interval' in configuration:
            short_average_interval = datetime.timedelta(seconds=int(configuration['short_average_interval']))

        assert short_average_interval < long_average_interval
        self._long_average_interval = long_average_interval
        self._short_average_interval = short_average_interval

        if 'delay' in configuration:
            self._delay = int(configuration['delay'])

    def get_seconds_delay_between_ticks(self) -> float:
        return self._delay

    def tick(self, markets: List[Market]) -> None:
        market = self._get_one_market(markets)

        try:
            self._check_and_process_open_orders(market)
            self._check_for_signal_and_trade(market)
            self._strategy_ticker += 1
        except NoCandlesForMarketInStorageException as e:
            raise SkipTickException('In given range: ' + str(e))

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {
            'long_average_interval': {
                'type': CONFIGURATION_STRUCTURE_TYPE_INT,
                'title': 'Long average time-delta',
                'default': str(DEFAULT_LONG_AVERAGE),
                'unit': 'seconds',
            },
            'short_average_interval': {
                'type': CONFIGURATION_STRUCTURE_TYPE_INT,
                'title': 'Short average time-delta',
                'default': str(DEFAULT_SHORT_AVERAGE),
                'unit': 'seconds',
            },
            'delay': {
                'type': CONFIGURATION_STRUCTURE_TYPE_INT,
                'title': 'Delay between checks',
                'default': '30',
                'unit': 'seconds',
            },
        }

    def _check_and_process_open_orders(self, market: Market):
        orders = self._order_storage.find_by(
            market_name=market.name,
            pair=self._strategy_run.pair,
            status=ORDER_STATUS_OPEN
        )
        for order in orders:
            status = market.get_order_status(order)
            if status.is_open is False:
                order.close(status.closed_at)
                self._order_storage.delete(order.order_id)
                self._order_storage.save_order(order)
                logger.info('Order "{}" has been successfully CLOSED.'.format(order.order_id))

    def _check_for_signal_and_trade(self, market: Market):
        signal = self._check_for_signal(market)
        if signal is not None:
            self._last_signal = signal

        if self._last_signal is not None:
            order = self._trade_on_signal(market)
            if order is not None:
                self._event_emitter.emit_new_order(self._order_storage.name, order)
                self._order_storage.save_order(order)

    def _does_trade_worth_it(self, market: Market) -> bool:
        last_order = self._order_storage.find_last_order(market.name, self._strategy_run.pair)
        if last_order is None:
            return True

        current_price = self.get_current_average_price(market)

        does_worth_it = absolute_possible_percentage_gain(last_order.rate, current_price) > market.transaction_taker_fee
        if not does_worth_it:
            logger.info('Skipping trade at current price: "{0:.8f}" (last order at: "{1:.8f}")'.format(
                current_price, last_order.rate
            ))

        return does_worth_it

    def _check_for_signal(self, market: Market) -> Union[Signal, None]:
        long_average, short_average = self._get_averages(market)
        current_sign = self._calculate_sign_of_change(long_average, short_average)
        current_average_price = self.get_current_average_price(market)

        logger.info(
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
            signal = self._create_signal(current_sign, current_average_price)

        self._previous_sign = current_sign
        return signal

    def get_current_average_price(self, market: Market):
        candle = self._candle_storage.get_last_minute_candle(
            market.name,
            self._strategy_run.pair,
            self._datetime_factory.now()
        )
        current_average_price = candle.average_price
        return current_average_price

    @staticmethod
    def _create_signal(current_sign: int, average_price: Decimal) -> Signal:
        assert current_sign in [-1, 1]
        return Signal(SIGNAL_BUY, average_price) if current_sign == 1 else Signal(SIGNAL_SELL, average_price)

    @staticmethod
    def _calculate_sign_of_change(long_average: Decimal, short_average: Decimal) -> int:
        diff = short_average - long_average
        if diff == 0:
            return 0

        return int(math.copysign(1, float(diff)))

    def _get_averages(self, market: Market) -> Tuple[Decimal, Decimal]:
        now = self._datetime_factory.now()

        long_average = self._candle_storage.mean(
            market.name,
            self._strategy_run.pair,
            CANDLE_STORAGE_FIELD_CLOSE,
            DateTimeInterval(now - self._long_average_interval, now)
        )

        short_average = self._candle_storage.mean(
            market.name,
            self._strategy_run.pair,
            CANDLE_STORAGE_FIELD_CLOSE,
            DateTimeInterval(now - self._short_average_interval, now)
        )

        return long_average, short_average

    def _trade_on_signal(self, market: Market) -> Union[Order, None]:
        logger.info('Checking trade on signal: "{}".'.format(self._last_signal))
        try:
            if self._last_signal.is_buy():
                self._cancel_open_order(market, DIRECTION_SELL)
                if self._does_trade_worth_it(market):
                    order = Order(
                        uuid.uuid4(),
                        self._strategy_run.strategy_run_id,
                        market.name,
                        DIRECTION_BUY,
                        self._datetime_factory.now(),
                        self._strategy_run.pair,
                        ORDER_TYPE_LIMIT,
                        market.calculate_maximal_amount_to_buy(
                            self._strategy_run.pair,
                            self._last_signal.average_price
                        ),
                        self._last_signal.average_price
                    )

                    market.place_order(order)
                    self._last_signal = None
                    return order

            elif self._last_signal.is_sell():
                self._cancel_open_order(market, DIRECTION_BUY)
                if self._does_trade_worth_it(market):
                    order = Order(
                        uuid.uuid4(),
                        self._strategy_run.strategy_run_id,
                        market.name,
                        DIRECTION_SELL,
                        self._datetime_factory.now(),
                        self._strategy_run.pair,
                        ORDER_TYPE_LIMIT,
                        market.calculate_maximal_amount_to_sell(self._strategy_run.pair),
                        self._last_signal.average_price
                    )

                    market.place_order(order)
                    self._last_signal = None
                    return order
            else:
                raise ValueError('Unknown signal: "{}"'.format(self._last_signal))  # pragma: no cover

        except NotEnoughBalanceToPerformOrderException as e:
            # Intentionally, this strategy does not need state of order,
            # just ignores buy/sell and waits for next signal.
            logger.warning(str(e))
            self._last_signal = None

        return None

    def _cancel_open_order(self, market: Market, direction: str):
        orders = self._order_storage.find_by(
            market_name=market.name,
            pair=self._strategy_run.pair,
            status=ORDER_STATUS_OPEN,
            direction=direction
        )
        for order in orders:
            try:
                market.cancel_order(order.id_on_market)
            except MarketException as e:
                logger.error('Order "{}" cancelling failed: Error: "{}"!'.format(order.order_id, e))
                return

            order.cancel(self._datetime_factory.now())
            self._order_storage.save_order(order)
            logger.info('Order "{}" has been CANCELED!'.format(order.order_id))

    @staticmethod
    def _get_one_market(markets: List[Market]) -> Market:
        if len(markets) != 1:
            message = 'This strategy works only with one market, {} given.'.format(len(markets))
            raise StrategyConfigurationException(message)
        return markets[0]
