from typing import Union, Tuple, List, Dict

import numpy

from coinrat.domain import Strategy, Pair, Market, MarketOrderException, StrategyConfigurationException, \
    DateTimeFactory, DateTimeInterval
from coinrat.domain.candle import Candle, CandleStorage, deserialize_candle_size, CandleSize
from coinrat.domain.order import Order, OrderStorage, DIRECTION_SELL, DIRECTION_BUY, ORDER_STATUS_OPEN, \
    NotEnoughBalanceToPerformOrderException
from coinrat.event.event_emitter import EventEmitter
from coinrat.domain.configuration_structure import CONFIGURATION_STRUCTURE_TYPE_STRING, CONFIGURATION_STRUCTURE_TYPE_INT
from .heikin_ashi_candle import HeikinAshiCandle

STRATEGY_NAME = 'heikin_ashi'
DEFAULT_CANDLE_SIZE_CONFIGURATION = '1-day'


class HeikinAshiStrategy(Strategy):
    """
    Reference:
        @link https://quantiacs.com/Blog/Intro-to-Algorithmic-Trading-with-Heikin-Ashi.aspx
        @link http://www.humbletraders.com/heikin-ashi-trading-strategy/
    """

    def get_seconds_delay_between_runs(self) -> float:
        return self._candle_size.get_as_time_delta().total_seconds()

    def __init__(
        self,
        candle_storage: CandleStorage,
        order_storage: OrderStorage,
        event_emitter: EventEmitter,
        datetime_factory: DateTimeFactory,
        configuration
    ) -> None:
        configuration = self.process_configuration(configuration)

        self._candle_storage = candle_storage
        self._order_storage = order_storage
        self._event_emitter = event_emitter
        self._datetime_factory = datetime_factory
        self._candle_size: CandleSize = configuration['candle_size']
        self._strategy_ticker = 0

        self._first_previous_candle: Union[HeikinAshiCandle, None] = None
        self._second_previous_candle: Union[HeikinAshiCandle, None] = None
        self._current_unfinished_candle: Union[HeikinAshiCandle, None] = None

    def tick(self, markets: List[Market], pair: Pair) -> None:
        if self._strategy_ticker == 0:
            self.first_tick(markets, pair)
        else:
            self._tick(markets, pair)

        self._strategy_ticker += 1

    def first_tick(self, markets: List[Market], pair: Pair) -> None:
        market = self.get_market(markets)

        start_time = self._datetime_factory.now()
        candles = self._candle_storage.find_by(
            market_name=market.name,
            pair=pair,
            interval=DateTimeInterval(start_time - 4 * self._candle_size.get_as_time_delta(), start_time),
            candle_size=self._candle_size
        )

        print(candles)

        assert len(candles) in [4, 5], \
            'Expected to get at 4 or 5 candles, but only {} given. Do you have enough data?'.format(len(candles))

        if len(candles) == 5:  # First and last candle can be cut in half, we dont need the first half-candle.
            candles.pop(0)

        first_candle = self.initial_candle_to_heikin_ashi(candles[0])
        self._second_previous_candle = self.candle_to_heikin_ashi(candles[1], first_candle)
        self._first_previous_candle = self.candle_to_heikin_ashi(candles[2], self._second_previous_candle)
        self._current_unfinished_candle = self.candle_to_heikin_ashi(candles[3], self._first_previous_candle)

    def _tick(self, markets: List[Market], pair: Pair) -> None:
        market = self.get_market(markets)
        current_time = self._datetime_factory.now()
        candles = self._candle_storage.find_by(
            market_name=market.name,
            pair=pair,
            interval=DateTimeInterval(current_time - 2 * self._candle_size.get_as_time_delta(), current_time),
            candle_size=self._candle_size
        )

        assert len(candles) in [2, 3], \
            'Expected to get at 2 or 3 candles, but only {} given. Do you have enough data?'.format(len(candles))

        if len(candles) == 3:  # First and last candle can be cut in half, we dont need the first half-candle.
            candles.pop(0)

        # print('current', self._current_unfinished_candle)
        # print('len: ', len(candles))
        # print(candles[0])
        # print(candles[1])
        # print('------------------------')

        if candles[0].time == self._current_unfinished_candle.time:
            self._second_previous_candle = self._first_previous_candle
            self._first_previous_candle = self.candle_to_heikin_ashi(candles[0], self._first_previous_candle)
            self._current_unfinished_candle = self.candle_to_heikin_ashi(candles[1], self._first_previous_candle)

            # print(self._second_previous_candle)
            # print(self._first_previous_candle)
            # print(self._first_previous_candle.has_upper_wick())

            if (
                self._first_previous_candle.is_bearish()
                and self._second_previous_candle.is_bearish()
                and self._first_previous_candle.body_size() > self._second_previous_candle.body_size()
                and not self._first_previous_candle.has_upper_wick()
            ):
                print('BUY !!!')

            if (
                self._first_previous_candle.is_bullish()
                and self._second_previous_candle.is_bullish()
                and self._first_previous_candle.body_size() > self._second_previous_candle.body_size()
                and not self._first_previous_candle.has_lower_wick()
            ):
                print('SELL !!!')

    @staticmethod
    def get_market(markets: List[Market]):
        if len(markets) != 1:
            raise ValueError('HeikinAshiStrategy expects exactly one market. But {} given.'.format(len(markets)))
        return markets[0]

    @staticmethod
    def initial_candle_to_heikin_ashi(candle: Candle) -> HeikinAshiCandle:
        return HeikinAshiCandle(
            candle.market_name,
            candle.pair,
            candle.time,
            open_price=(candle.open + candle.high + candle.low + candle.close) / 4,
            high_price=candle.high,
            low_price=candle.low,
            close_price=(candle.open + candle.close) / 2,
            candle_size=candle.candle_size
        )

    @staticmethod
    def candle_to_heikin_ashi(candle: Candle, previous: HeikinAshiCandle) -> HeikinAshiCandle:
        heikin_close = (candle.open + candle.high + candle.low + candle.close) / 4
        heikin_open = (previous.open + previous.close) / 2
        elements = numpy.array([candle.high, candle.low, heikin_open, heikin_close])
        heikin_high = elements.max(0)
        heikin_low = elements.min(0)

        return HeikinAshiCandle(
            candle.market_name,
            candle.pair,
            candle.time,
            heikin_close,
            heikin_high,
            heikin_low,
            heikin_open,
            candle.candle_size
        )

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        return {
            'candle_size': {
                'type': CONFIGURATION_STRUCTURE_TYPE_STRING,
                'title': 'Candle size',
                'default': DEFAULT_CANDLE_SIZE_CONFIGURATION,
                'unit': '',
            },
            'delay': {
                'type': CONFIGURATION_STRUCTURE_TYPE_INT,
                'title': 'Disable sleep by setting this to 0',
                'default': 1,
                'unit': 'seconds',
                'hidden': True,
            },
        }

    @staticmethod
    def process_configuration(configuration: Dict) -> Dict:
        if 'candle_size' not in configuration:
            configuration['candle_size'] = DEFAULT_CANDLE_SIZE_CONFIGURATION

        configuration['candle_size'] = deserialize_candle_size(configuration['candle_size'])

        return configuration
