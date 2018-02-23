import datetime
import logging
from typing import List, Dict
from decimal import Decimal
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair, serialize_pair
from coinrat.domain.candle import Candle, CandleStorage, \
    CANDLE_STORAGE_FIELD_HIGH, CANDLE_STORAGE_FIELD_OPEN, CANDLE_STORAGE_FIELD_CLOSE, CANDLE_STORAGE_FIELD_LOW, \
    NoCandlesForMarketInStorageException, CANDLE_STORAGE_FIELD_MARKET, CANDLE_STORAGE_FIELD_PAIR, CandleSize, \
    CANDLE_SIZE_UNIT_MINUTE, serialize_candle_size, CANDLE_STORAGE_FIELD_SIZE, deserialize_candle, \
    CANDLE_SIZE_UNIT_DAY, CANDLE_SIZE_UNIT_HOUR

CANDLE_STORAGE_NAME = 'influx_db'
MEASUREMENT_CANDLES_NAME = 'candles'

UNIT_MAP = {
    CANDLE_SIZE_UNIT_MINUTE: 'm',
    CANDLE_SIZE_UNIT_HOUR: 'h',
    CANDLE_SIZE_UNIT_DAY: 'd',
}

logger = logging.getLogger(__name__)


class CandleInnoDbStorage(CandleStorage):
    def __init__(self, influx_db_client: InfluxDBClient) -> None:
        self._client = influx_db_client

    @property
    def name(self) -> str:
        return CANDLE_STORAGE_NAME

    def write_candle(self, candle: Candle) -> None:
        self.write_candles([candle])

    def write_candles(self, candles: List[Candle]) -> None:
        if len(candles) == 0:
            return
        self._client.write_points([self._create_point_data(candle) for candle in candles])
        logger.debug('Into market "{}", {} candles inserted'.format(candles[0].market_name, len(candles)))

    def find_by(
        self,
        market_name: str,
        pair: Pair,
        interval: DateTimeInterval = DateTimeInterval(None, None),
        candle_size: CandleSize = CandleSize(CANDLE_SIZE_UNIT_MINUTE, 1)
    ) -> List[Candle]:
        parameters = {
            CANDLE_STORAGE_FIELD_MARKET: "= '{}'".format(market_name),
            CANDLE_STORAGE_FIELD_PAIR: "= '{}'".format(serialize_pair(pair)),
        }
        if interval.since is not None:
            parameters['"time" >'] = "'{}'".format(interval.since.isoformat())

        if interval.till is not None:
            parameters['"time" <'] = "'{}'".format(interval.till.isoformat())

        select = '*'
        if not candle_size.is_one_minute():
            select = 'FIRST("open") AS "open", MAX("high") AS "high", MIN("low") AS "low", LAST("close") AS "close"'

        sql = 'SELECT {} FROM "{}" WHERE '.format(select, MEASUREMENT_CANDLES_NAME)
        where = []
        for key, value in parameters.items():
            where.append('{} {}'.format(key, value))
        sql += ' AND '.join(where)
        sql += self._get_group_by(candle_size)

        result: ResultSet = self._client.query(sql)
        data = list(result.get_points())

        return self._parse_db_result_into_candles(data, market_name, pair, candle_size)

    @staticmethod
    def _parse_db_result_into_candles(
        data: List[Dict],
        market_name: str,
        pair: Pair,
        candle_size: CandleSize
    ) -> List[Candle]:
        candles = []
        for raw_candle in data:
            if (raw_candle[CANDLE_STORAGE_FIELD_OPEN] is None
                and raw_candle[CANDLE_STORAGE_FIELD_OPEN] is None
                and raw_candle[CANDLE_STORAGE_FIELD_OPEN] is None
                and raw_candle[CANDLE_STORAGE_FIELD_OPEN] is None
            ):
                continue

            raw_candle = CandleInnoDbStorage._fix_fields_in_raw_candle(raw_candle, market_name, pair, candle_size)
            candles.append(deserialize_candle(raw_candle))

        return candles

    @staticmethod
    def _fix_fields_in_raw_candle(raw_candle: Dict, market_name: str, pair: Pair, candle_size: CandleSize) -> Dict:
        if CANDLE_STORAGE_FIELD_MARKET not in raw_candle:
            raw_candle[CANDLE_STORAGE_FIELD_MARKET] = market_name
        if CANDLE_STORAGE_FIELD_PAIR not in raw_candle:
            raw_candle[CANDLE_STORAGE_FIELD_PAIR] = serialize_pair(pair)
        if CANDLE_STORAGE_FIELD_SIZE not in raw_candle:
            raw_candle[CANDLE_STORAGE_FIELD_SIZE] = serialize_candle_size(candle_size)

        return raw_candle

    @staticmethod
    def _get_group_by(candle_size: CandleSize) -> str:
        if candle_size.is_one_minute():
            return ''
        return ' GROUP BY time({}{})'.format(candle_size.size, UNIT_MAP[candle_size.unit])

    def get_last_minute_candle(self, market_name: str, pair: Pair, current_time: datetime.datetime) -> Candle:
        sql = '''
            SELECT * FROM "{}" WHERE "pair"='{}' AND "market"='{}' AND "time" <= '{}' ORDER BY "time" DESC LIMIT 1
        '''.format(MEASUREMENT_CANDLES_NAME, serialize_pair(pair), market_name, current_time.isoformat())

        result: ResultSet = self._client.query(sql)
        result = list(result.get_points())
        self._validate_result_has_some_data(market_name, result)

        return deserialize_candle(result[0])

    def mean(
        self,
        market_name: str,
        pair: Pair,
        field: str,
        interval: DateTimeInterval = DateTimeInterval(None, None)
    ) -> Decimal:
        sql = '''
            SELECT MEAN("{}") AS "field_mean" 
            FROM "{}" WHERE "time" > '{}' AND "time" < '{}' AND "pair"='{}' AND "market"='{}' 
            GROUP BY "{}"
        '''.format(
            field,
            MEASUREMENT_CANDLES_NAME,
            interval.since.isoformat(),
            interval.till.isoformat(),
            serialize_pair(pair),
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
    def _create_point_data(candle: Candle):
        return {
            'measurement': MEASUREMENT_CANDLES_NAME,
            'tags': {
                'market': candle.market_name,
                'pair': serialize_pair(candle.pair),
            },
            'time': candle.time.isoformat(),
            'fields': {
                CANDLE_STORAGE_FIELD_OPEN: float(candle.open),
                CANDLE_STORAGE_FIELD_CLOSE: float(candle.close),
                CANDLE_STORAGE_FIELD_LOW: float(candle.low),
                CANDLE_STORAGE_FIELD_HIGH: float(candle.high),
                CANDLE_STORAGE_FIELD_SIZE: serialize_candle_size(candle.candle_size)
            }
        }
