import logging
from typing import List
from influxdb import InfluxDBClient

from coinrat.market import MinuteCandle, MarketStorage


class MarketInnoDbStorage(MarketStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def write_candle(self, market: str, candle: MinuteCandle) -> None:
        self.write_candles(market, [candle])

    def write_candles(self, market: str, candles: List[MinuteCandle]) -> None:
        self._client.write_points([self._transform_into_raw_data(market, candle) for candle in candles])
        candles_time_marks = ','.join(map(lambda c: c.time.isoformat(), candles))
        logging.debug('Candles for "{}" inserted: [{}]'.format(market, candles_time_marks))

    @staticmethod
    def _transform_into_raw_data(market: str, candle: MinuteCandle):
        return {
            "measurement": "candles",
            "tags": {
                "market": market,
            },
            "time": candle.time.isoformat(),
            "fields": {
                'open': '{:.8f}'.format(candle.open),
                'close': '{:.8f}'.format(candle.close),
                'low': '{:.8f}'.format(candle.low),
                'high': '{:.8f}'.format(candle.high),
            }
        }


def market_storage_factory(
    database: str,
    host: str = 'localhost',
    port: int = 8086,
    user: str = 'root',
    password: str = 'root',
):
    return MarketInnoDbStorage(InfluxDBClient(host, port, user, password, database))
