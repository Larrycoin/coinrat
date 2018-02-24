import logging

import MySQLdb
import datetime
import json
from typing import List
from uuid import UUID

from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import serialize_pair, deserialize_pair
from .strategy_run import StrategyRun, serialize_strategy_run_markets, deserialize_strategy_run_markets

logger = logging.getLogger(__name__)


class StrategyRunStorage:
    def __init__(self, connection: MySQLdb.Connection) -> None:
        self._connection = connection

    def update(self, strategy_run: StrategyRun):
        self._connection.begin()
        cursor = self._connection.cursor()
        cursor.execute('DELETE FROM `strategy_runs` WHERE `id` = %s', (strategy_run.strategy_run_id,))
        self._insert(cursor, strategy_run)
        cursor.close()
        self._connection.commit()
        logger.debug('Strategy Run: {} updated.'.format(strategy_run.strategy_run_id))

    def insert(self, strategy_run: StrategyRun):
        self._connection.begin()
        cursor = self._connection.cursor()
        self._insert(cursor, strategy_run)
        cursor.close()
        self._connection.commit()
        logger.debug('Strategy Run: {} saved.'.format(strategy_run.strategy_run_id))

    @staticmethod
    def _insert(cursor, strategy_run: StrategyRun) -> None:
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
            str(strategy_run.strategy_run_id),
            strategy_run.run_at.timestamp(),
            serialize_pair(strategy_run.pair),
            json.dumps(serialize_strategy_run_markets(strategy_run.markets)),
            strategy_run.strategy_name,
            json.dumps(strategy_run.strategy_configuration),
            strategy_run.interval.since.timestamp(),
            strategy_run.interval.till.timestamp() if strategy_run.interval.till is not None else None,
            strategy_run.candle_storage_name,
            strategy_run.order_storage_name
        ))

    def find_by(self) -> List[StrategyRun]:
        self._connection.begin()
        cursor = self._connection.cursor()
        cursor.execute('SELECT * FROM `strategy_runs` ORDER BY `run_at` DESC')

        result = []
        for row in cursor.fetchall():
            result.append(StrategyRun(
                UUID(row[0]),
                datetime.datetime.fromtimestamp(row[1], tz=datetime.timezone.utc),
                deserialize_pair(row[2]),
                deserialize_strategy_run_markets(json.loads(row[3])),
                row[4],
                json.loads(row[5]),
                DateTimeInterval(
                    datetime.datetime.fromtimestamp(row[6], tz=datetime.timezone.utc),
                    datetime.datetime.fromtimestamp(row[7], tz=datetime.timezone.utc) \
                        if row[7] is not None else None,
                ),
                row[8],
                row[9],
            ))
        cursor.close()
        self._connection.commit()

        return result
