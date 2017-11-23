import datetime
import logging
from typing import List, Tuple, Union, Generator

from decimal import Decimal
from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import MinuteCandle, MarketsCandleStorage, MarketPair, CANDLE_STORAGE_FIELD_HIGH, \
    CANDLE_STORAGE_FIELD_OPEN, CANDLE_STORAGE_FIELD_CLOSE, CANDLE_STORAGE_FIELD_LOW


class MarketInnoDbStorage(MarketsCandleStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def write_candle(self, candle: MinuteCandle) -> None:
        self.write_candles([candle])

    def write_candles(self, candles: Union[Generator[MinuteCandle, None, None], List[MinuteCandle]]) -> None:
        self._client.write_points([self._transform_into_raw_data(candle) for candle in candles])
        candles = candles[-20:]
        candles_time_marks = ','.join(map(lambda c: c.time.isoformat(), candles))
        logging.debug('Candles for "{}" inserted: [{}]'.format(candles[0].market_name, candles_time_marks))

    def mean(
        self,
        market_name: str,
        pair: MarketPair,
        field: str,
        interval: Tuple[datetime.datetime, datetime.datetime]
    ) -> Decimal:
        assert '+00:00' in interval[0].isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(interval[0].isoformat()))
        assert '+00:00' in interval[0].isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(interval[1].isoformat()))

        sql = '''
            SELECT MEAN("{}") AS "field_mean" 
            FROM "candles" WHERE "time" > '{}' AND "time" < '{}' AND "pair"='{}' AND "market"='{}' 
            GROUP BY "{}"
        '''.format(
            field,
            interval[0].isoformat(),
            interval[1].isoformat(),
            self._create_pair_identifier(pair),
            market_name,
            field
        )
        result: ResultSet = self._client.query(sql)
        mean = list(result.items()[0][1])[0]['field_mean']
        return Decimal(mean)

    @staticmethod
    def _transform_into_raw_data(candle: MinuteCandle):
        return {
            "measurement": "candles",
            "tags": {
                "market": candle.market_name,
                "pair": MarketInnoDbStorage._create_pair_identifier(candle.pair),
            },
            "time": candle.time.isoformat(),
            "fields": {
                # Todo: figure out how to store decimals in influx (maybe int -> *100000)
                CANDLE_STORAGE_FIELD_OPEN: float(candle.open),
                CANDLE_STORAGE_FIELD_CLOSE: float(candle.close),
                CANDLE_STORAGE_FIELD_LOW: float(candle.low),
                CANDLE_STORAGE_FIELD_HIGH: float(candle.high),
            }
        }

    @staticmethod
    def _create_pair_identifier(pair: MarketPair) -> str:
        return '{}_{}'.format(pair.left, pair.right)


def market_storage_factory(
    database: str,
    host: str = 'localhost',
    port: int = 8086,
    user: str = 'root',
    password: str = 'root',
):
    return MarketInnoDbStorage(InfluxDBClient(host, port, user, password, database))
