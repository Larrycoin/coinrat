import MySQLdb
import datetime
import json
from typing import List
from uuid import UUID

from coinrat.domain import DateTimeInterval
from coinrat.domain.strategy import StrategyRun, StrategyRunMarket
from coinrat.domain.pair import serialize_pair, deserialize_pair


class StrategyRunStorage:
    def __init__(self, connection: MySQLdb.Connection) -> None:
        self._connection = connection

    def save(self, strategy_run: StrategyRun):
        serialized_markets = {}

        for strategy_run_market in strategy_run.markets:
            serialized_markets[strategy_run_market.market_name] = strategy_run_market.market_configuration

        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT INTO `strategy_runs` (
                `id`,
                `run_at`,
                `pair`,
                `markets`,
                `strategy_name`,
                `strategy_configuration`,
                `interval_since`,
                `interval_till`,
                `candle_storage_name`,
                `order_storage_name`
            ) VALUES (
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s,
                %s
            )     
        """, (
            str(strategy_run.strategy_id),
            strategy_run.run_at.timestamp(),
            serialize_pair(strategy_run.pair),
            json.dumps(serialized_markets),
            strategy_run.strategy_name,
            json.dumps(strategy_run.strategy_configuration),
            strategy_run.interval.since.timestamp(),
            strategy_run.interval.till.timestamp(),
            strategy_run.candle_storage_name,
            strategy_run.order_storage_name
        ))

    def find_by(self) -> List[StrategyRun]:
        cursor = self._connection.cursor()
        cursor.execute('SELECT * FROM `strategy_runs`')

        result = []
        for row in cursor.fetchall():
            strategy_run_markets = [
                StrategyRunMarket(market_name, market_configuration)
                for market_name, market_configuration in json.loads(row[3]).items()
            ]

            result.append(StrategyRun(
                UUID(row[0]),
                datetime.datetime.fromtimestamp(row[1], tz=datetime.timezone.utc),
                deserialize_pair(row[2]),
                strategy_run_markets,
                row[4],
                json.loads(row[5]),
                DateTimeInterval(
                    datetime.datetime.fromtimestamp(row[6], tz=datetime.timezone.utc),
                    datetime.datetime.fromtimestamp(row[7], tz=datetime.timezone.utc),
                ),
                row[8],
                row[9],
            ))
        return result
