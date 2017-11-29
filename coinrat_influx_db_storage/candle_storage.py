import datetime
import logging
from typing import List, Tuple, Union, Generator, Dict
import dateutil.parser
from decimal import Decimal
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import MinuteCandle, CandleStorage, Pair, CANDLE_STORAGE_FIELD_HIGH, \
    CANDLE_STORAGE_FIELD_OPEN, CANDLE_STORAGE_FIELD_CLOSE, CANDLE_STORAGE_FIELD_LOW, \
    NoCandlesForMarketInStorageException
from .utils import create_pair_identifier

CANDLE_STORAGE_NAME = 'influx_db'
MEASUREMENT_CANDLES_NAME = 'candles'

CANDLE_STORAGE_FIELD_MARKET = 'market'
CANDLE_STORAGE_FIELD_PAIR = 'pair'


class CandleInnoDbStorage(CandleStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def write_candle(self, candle: MinuteCandle) -> None:
        self.write_candles([candle])

    def write_candles(self, candles: Union[Generator[MinuteCandle, None, None], List[MinuteCandle]]) -> None:
        if len(candles) == 0:
            return
        self._client.write_points([self._transform_into_raw_data(candle) for candle in candles])
        logging.debug('Into market "{}", {} candles inserted'.format(candles[0].market_name, len(candles)))

    def get_current_candle(self, market_name: str, pair: Pair) -> MinuteCandle:
        sql = '''
            SELECT * FROM "{}" WHERE "pair"='{}' AND "market"='{}' ORDER BY "time" DESC LIMIT 1
        '''.format(MEASUREMENT_CANDLES_NAME, create_pair_identifier(pair), market_name)

        result: ResultSet = self._client.query(sql)
        result = list(result.get_points())
        self._validate_result_has_some_data(market_name, result)

        return self._create_candle_from_serialized(result[0])

    def mean(
        self,
        market_name: str,
        pair: Pair,
        field: str,
        interval: Tuple[datetime.datetime, datetime.datetime]
    ) -> Decimal:
        assert '+00:00' in interval[0].isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(interval[0].isoformat()))
        assert '+00:00' in interval[0].isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(interval[1].isoformat()))

        sql = '''
            SELECT MEAN("{}") AS "field_mean" 
            FROM "{}" WHERE "time" > '{}' AND "time" < '{}' AND "pair"='{}' AND "market"='{}' 
            GROUP BY "{}"
        '''.format(
            field,
            MEASUREMENT_CANDLES_NAME,
            interval[0].isoformat(),
            interval[1].isoformat(),
            create_pair_identifier(pair),
            market_name,
            field
        )
        result: ResultSet = self._client.query(sql)
        self._validate_result_has_some_data(market_name, result)
        mean = list(result.items()[0][1])[0]['field_mean']
        return Decimal(mean)

    @staticmethod
    def _validate_result_has_some_data(market_name: str, result: ResultSet) -> None:
        if len(result) == 0:
            raise NoCandlesForMarketInStorageException(
                'For market "{}" no candles in storage "{}".'.format(market_name, CANDLE_STORAGE_NAME)
            )

    @staticmethod
    def _transform_into_raw_data(candle: MinuteCandle):
        return {
            'measurement': MEASUREMENT_CANDLES_NAME,
            'tags': {
                'market': candle.market_name,
                'pair': create_pair_identifier(candle.pair),
            },
            'time': candle.time.isoformat(),
            'fields': {
                # Todo: figure out how to store decimals in influx (maybe int -> *100000)
                CANDLE_STORAGE_FIELD_OPEN: float(candle.open),
                CANDLE_STORAGE_FIELD_CLOSE: float(candle.close),
                CANDLE_STORAGE_FIELD_LOW: float(candle.low),
                CANDLE_STORAGE_FIELD_HIGH: float(candle.high),
            }
        }

    @staticmethod
    def _create_candle_from_serialized(row: Dict) -> MinuteCandle:
        pair_data = row[CANDLE_STORAGE_FIELD_PAIR].split('_')

        return MinuteCandle(
            row[CANDLE_STORAGE_FIELD_MARKET],
            Pair(pair_data[0], pair_data[1]),
            dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc),
            Decimal(row[CANDLE_STORAGE_FIELD_OPEN]),
            Decimal(row[CANDLE_STORAGE_FIELD_HIGH]),
            Decimal(row[CANDLE_STORAGE_FIELD_LOW]),
            Decimal(row[CANDLE_STORAGE_FIELD_CLOSE])
        )