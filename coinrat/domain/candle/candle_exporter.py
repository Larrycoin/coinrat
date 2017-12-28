import datetime
import json
import dateutil.parser
from typing import Dict

from decimal import Decimal

from coinrat.domain import Pair, DateTimeInterval
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
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ):
        candles = self._candle_storage.find_by(market_name=market_name, pair=pair, interval=interval)
        data = list(map(self.serialize_candle_to_json_serializable, candles))

        with open(filename, 'w') as outfile:
            json.dump(data, outfile)

    def import_from_file(self, filename: str):
        with open(filename) as json_file:
            data = json.load(json_file)
            candles = list(map(self.create_candle_from_data, data))
            self._candle_storage.write_candles(candles)

    @staticmethod
    def serialize_candle_to_json_serializable(candle: MinuteCandle):
        return {
            'market': candle.market_name,
            'pair': CandleExporter._create_pair_identifier(candle.pair),
            'time': candle.time.isoformat(),
            CANDLE_STORAGE_FIELD_OPEN: str(candle.open),
            CANDLE_STORAGE_FIELD_HIGH: str(candle.high),
            CANDLE_STORAGE_FIELD_LOW: str(candle.low),
            CANDLE_STORAGE_FIELD_CLOSE: str(candle.close),
        }

    @staticmethod
    def create_candle_from_data(row: Dict) -> MinuteCandle:
        return MinuteCandle(
            row['market'],
            CandleExporter._create_pair_from_identifier(row['pair']),
            dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc),
            Decimal(row[CANDLE_STORAGE_FIELD_OPEN]),
            Decimal(row[CANDLE_STORAGE_FIELD_HIGH]),
            Decimal(row[CANDLE_STORAGE_FIELD_LOW]),
            Decimal(row[CANDLE_STORAGE_FIELD_CLOSE])
        )

    @staticmethod
    def _create_pair_identifier(pair: Pair) -> str:
        return '{}_{}'.format(pair.base_currency, pair.market_currency)

    @staticmethod
    def _create_pair_from_identifier(identifier: str) -> Pair:
        return Pair(*identifier.split('_'))
