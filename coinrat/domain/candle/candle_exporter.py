import datetime
import json

from coinrat.domain.pair import Pair
from .candle import MinuteCandle

from .candle_storage import CandleStorage, \
    CANDLE_STORAGE_FIELD_OPEN, CANDLE_STORAGE_FIELD_CLOSE, CANDLE_STORAGE_FIELD_LOW, CANDLE_STORAGE_FIELD_HIGH


class CandleExporter:
    def __init__(self, candle_storage: CandleStorage) -> None:
        self._candle_storage = candle_storage

    def export_to_file(
        self,
        filename: str,
        market_name: str,
        pair: Pair,
        since: datetime = None,
        till: datetime = None
    ):
        assert since is None or till is None or since < till  # todo: introduce interval value object

        candles = self._candle_storage.find_by(market_name=market_name, pair=pair, since=since, till=till)
        data = list(map(self._serialize_candle_to_json_serializable, candles))

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    @staticmethod
    def _serialize_candle_to_json_serializable(candle: MinuteCandle):
        return {
            'market': candle.market_name,
            'pair': candle.pair.base_currency + '_' + candle.pair.market_currency,
            'time': candle.time.isoformat(),
            CANDLE_STORAGE_FIELD_OPEN: float(candle.open),
            CANDLE_STORAGE_FIELD_CLOSE: float(candle.close),
            CANDLE_STORAGE_FIELD_LOW: float(candle.low),
            CANDLE_STORAGE_FIELD_HIGH: float(candle.high),
        }
