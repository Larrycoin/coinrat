import json

from coinrat.domain import Pair, DateTimeInterval
from .candle import serialize_candles, deserialize_candles

from .candle_storage import CandleStorage


class CandleExporter:
    def __init__(self, candle_storage: CandleStorage) -> None:
        self._candle_storage = candle_storage

    def export_to_file(
        self,
        filename: str,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ):
        candles = self._candle_storage.find_by(market_name=market_name, pair=pair, interval=interval)
        data = serialize_candles(candles)

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def import_from_file(self, filename: str):
        with open(filename) as json_file:
            data = json.load(json_file)
            candles = deserialize_candles(data)
            self._candle_storage.write_candles(candles)
