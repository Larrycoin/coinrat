from typing import List

from influxdb import InfluxDBClient

from coinrat_market import Candle


class MarketStorage:
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def write_candle(self, market: str, candle: Candle) -> None:
        self.write_candles(market, [candle])

    def write_candles(self, market: str, candles: List[Candle]) -> None:
        self._client.write_points([self._transform_into_raw_data(market, candle) for candle in candles])

    @staticmethod
    def _transform_into_raw_data(market: str, candle: Candle):
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
    return MarketStorage(InfluxDBClient(host, port, user, password, database))
