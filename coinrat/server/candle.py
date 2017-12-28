from typing import Dict, List

from coinrat.domain.candle import MinuteCandle
from coinrat.domain.candle import CandleExporter


def serialize_candle(candle: MinuteCandle) -> Dict:
    return CandleExporter.serialize_candle_to_json_serializable(candle)


def serialize_candles(candles: List[MinuteCandle]) -> List[Dict]:
    return list(map(serialize_candle, candles))


def parse_candle(data: Dict) -> MinuteCandle:
    return CandleExporter.create_candle_from_data(data)
