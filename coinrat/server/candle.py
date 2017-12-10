from typing import Dict, List

from coinrat.domain.candle import MinuteCandle


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
