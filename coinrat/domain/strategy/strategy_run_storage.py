import json

import MySQLdb

from coinrat.domain.strategy import StrategyRun


class StrategyRunStorage:
    def __init__(self, connection: MySQLdb.Connection) -> None:
        self._connection = connection

    def save(self, strategy_run: StrategyRun):
        cursor = self._connection.cursor()
        cursor.execute("""
            INSERT INTO `strategy_runs` (
                `id`,
                `run_at`,
                `market_name`,
                `market_configuration`,
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
            strategy_run.market_name,
            json.dumps(strategy_run.market_configuration),
            strategy_run.strategy_name,
            json.dumps(strategy_run.strategy_configuration),
            strategy_run.interval.since.timestamp(),
            strategy_run.interval.till.timestamp(),
            strategy_run.candle_storage_name,
            strategy_run.order_storage_name
        ))
