import datetime
import dateutil.parser

from typing import Dict, List

from decimal import Decimal

from coinrat.domain.candle import MinuteCandle
from .pair import parse_pair


def serialize_candle(candle: MinuteCandle) -> Dict:
    return {
        'market': candle.market_name,
        'pair': '{}_{}'.format(candle.pair.base_currency, candle.pair.market_currency),
        'time': candle.time.isoformat(),
        'open': float(candle.open),
        'close': float(candle.close),
        'low': float(candle.low),
        'high': float(candle.high),
    }


def serialize_candles(candles: List[MinuteCandle]) -> List[Dict]:
    return list(map(serialize_candle, candles))


def parse_candle(data: Dict) -> MinuteCandle:
    pair_data = data['pair']

    return MinuteCandle(
        data['market'],
        parse_pair(pair_data),
        dateutil.parser.parse(data['time']).replace(tzinfo=datetime.timezone.utc),
        Decimal(data['open']),
        Decimal(data['close']),
        Decimal(data['low']),
        Decimal(data['high'])
    )
