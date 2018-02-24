import logging
import uuid
from typing import Union, List, Dict, cast

from decimal import Decimal

from coinrat.domain import DateTimeFactory, DateTimeInterval
from coinrat.domain.market import Market
from coinrat.domain.strategy import Strategy, StrategyRun, SkipTickException
from coinrat.domain.candle import CandleStorage, deserialize_candle_size, CandleSize
from coinrat.domain.order import Order, OrderStorage, DIRECTION_SELL, DIRECTION_BUY, ORDER_TYPE_LIMIT, \
    NotEnoughBalanceToPerformOrderException
from coinrat.event.event_emitter import EventEmitter
from coinrat.domain.configuration_structure import CONFIGURATION_STRUCTURE_TYPE_CANDLE_SIZE
from coinrat_heikin_ashi_strategy.heikin_ashi_candle import HeikinAshiCandle, candle_to_heikin_ashi, \
    create_initial_heikin_ashi_candle
from coinrat.domain.configuration_structure import format_data_to_python_types

logger = logging.getLogger(__name__)

STRATEGY_NAME = 'heikin_ashi'
DEFAULT_CANDLE_SIZE_CONFIGURATION = '1-day'


class HeikinAshiStrategy(Strategy):
    """
    Reference:
        @link https://quantiacs.com/Blog/Intro-to-Algorithmic-Trading-with-Heikin-Ashi.aspx
        @link http://www.humbletraders.com/heikin-ashi-trading-strategy/
    """

    def __init__(
        self,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        event_emitter: EventEmitter,
        datetime_factory: DateTimeFactory,
        strategy_run: StrategyRun
    ) -> None:
        configuration = self.process_configuration(strategy_run.strategy_configuration)

        self._candle_storage = candle_storage
        self._order_storage = order_storage
        self._event_emitter = event_emitter
        self._datetime_factory = datetime_factory
        self._candle_size = cast(CandleSize, configuration['candle_size'])
        self._strategy_ticker = 0

        self._first_previous_candle: Union[HeikinAshiCandle, None] = None
        self._second_previous_candle: Union[HeikinAshiCandle, None] = None
        self._current_unfinished_candle: Union[HeikinAshiCandle, None] = None
        self._trend = 0
        self._strategy_run = strategy_run

    def get_seconds_delay_between_ticks(self) -> float:
        return self._candle_size.get_as_time_delta().total_seconds()

    def tick(self, markets: List[Market]) -> None:
        if self._strategy_ticker == 0:
            self.first_tick_initialize_strategy_data(markets)
        else:
            self._tick(markets)

        self._strategy_ticker += 1

    def first_tick_initialize_strategy_data(self, markets: List[Market]) -> None:
        market = self.get_market(markets)

        current_time = self._datetime_factory.now()
        interval = DateTimeInterval(current_time - 4 * self._candle_size.get_as_time_delta(), current_time)

        candles = self._candle_storage.find_by(
            market_name=market.name,
            pair=self._strategy_run.pair,
            interval=interval,
            candle_size=self._candle_size
        )

        if len(candles) not in [4, 5]:
            raise SkipTickException(
                'Expected to get at 4 or 5 candles, but only {} given. Do you have enough data?'.format(len(candles))
            )

        if len(candles) == 5:  # First and last candle can be cut in half, we dont need the first half-candle.
            candles.pop(0)

        first_candle = create_initial_heikin_ashi_candle(candles[0])
        self._second_previous_candle = candle_to_heikin_ashi(candles[1], first_candle)
        self._first_previous_candle = candle_to_heikin_ashi(candles[2], self._second_previous_candle)
        self._current_unfinished_candle = candle_to_heikin_ashi(candles[3], self._first_previous_candle)

    def _tick(self, markets: List[Market]) -> None:

        market = self.get_market(markets)
        current_time = self._datetime_factory.now()
        interval = DateTimeInterval(current_time - 2 * self._candle_size.get_as_time_delta(), current_time)

        candles = self._candle_storage.find_by(
            market_name=market.name,
            pair=self._strategy_run.pair,
            interval=interval,
            candle_size=self._candle_size
        )

        if len(candles) not in [2, 3]:
            raise SkipTickException(
                'Expected to get at 2 or 3 candles, but only {} given. Do you have enough data?'.format(len(candles))
            )

        if len(candles) == 3:  # First and last candle can be cut in half, we don't need the first half-candle.
            candles.pop(0)

        self.update_trend()

        if candles[0].time == self._current_unfinished_candle.time:
            self._second_previous_candle = self._first_previous_candle
            self._first_previous_candle = candle_to_heikin_ashi(candles[0], self._first_previous_candle)
            self._current_unfinished_candle = candle_to_heikin_ashi(candles[1], self._first_previous_candle)

            self.log_tick()

            try:
                self.check_for_buy_or_sell(market)
            except NotEnoughBalanceToPerformOrderException as e:
                # Intentionally, this strategy does not need state of order,
                # just ignores buy/sell and waits for next signal.
                logger.warning(str(e))

    def update_trend(self):
        if self._second_previous_candle.is_bearish() and self._trend > -5:
            self._trend -= 1
        if self._second_previous_candle.is_bullish() and self._trend < 5:
            self._trend += 1

    def check_for_buy_or_sell(self, market: Market) -> None:
        if (
            self._trend >= 5
            and self._first_previous_candle.is_bearish()
            and self._second_previous_candle.is_bearish()
        ):
            self.create_order(market, DIRECTION_SELL)
        if (
            self._trend <= 5
            and self._first_previous_candle.is_bullish()
            and self._second_previous_candle.is_bullish()
        ):
            self.create_order(market, DIRECTION_BUY)

    def create_order(self, market: Market, direction: str):
        current_price = market.get_current_price(self._strategy_run.pair)
        logger.info(direction.upper() + 'ING at price: ' + str(current_price))
        order = Order(
            uuid.uuid4(),
            self._strategy_run.strategy_run_id,
            market.name,
            direction,
            self._datetime_factory.now(),
            self._strategy_run.pair,
            ORDER_TYPE_LIMIT,
            market.calculate_maximal_amount_to_buy(self._strategy_run.pair, current_price) \
                if direction is DIRECTION_BUY \
                else market.calculate_maximal_amount_to_sell(self._strategy_run.pair),
            current_price
        )
        market.place_order(order)
        self._event_emitter.emit_new_order(self._order_storage.name, order)
        self._order_storage.save_order(order)

    def log_tick(self) -> None:
        logger.info(
            '[{0}] {1} | Trend: {2}, HA_Candle(-1): {3}, HA_Candle(0): {4}`, '.format(
                self._current_unfinished_candle.time.isoformat(),
                self._strategy_ticker,
                self._trend,
                'BEAR' if self._first_previous_candle.is_bearish() else 'BULL',
                'BEAR' if self._second_previous_candle.is_bearish() else 'BULL'
            )
        )

    @staticmethod
    def get_market(markets: List[Market]):
        if len(markets) != 1:
            raise ValueError('HeikinAshiStrategy expects exactly one market. But {} given.'.format(len(markets)))
        return markets[0]

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {
            'candle_size': {
                'type': CONFIGURATION_STRUCTURE_TYPE_CANDLE_SIZE,
                'title': 'Candle size',
                'default': DEFAULT_CANDLE_SIZE_CONFIGURATION,
                'unit': '',
            }
        }

    def process_configuration(self, configuration: Dict[str, str]) -> Dict[str, Union[str, int, Decimal, CandleSize]]:
        configuration_formatted = cast(
            Dict[str, Union[str, int, Decimal, CandleSize]],
            format_data_to_python_types(configuration, self.get_configuration_structure())
        )

        if 'candle_size' not in configuration_formatted:
            configuration_formatted['candle_size'] = DEFAULT_CANDLE_SIZE_CONFIGURATION

        configuration_formatted['candle_size'] = deserialize_candle_size(str(configuration_formatted['candle_size']))

        return configuration_formatted
