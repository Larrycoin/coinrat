from typing import Dict, List

from decimal import Decimal
from uuid import UUID

import datetime
import dateutil.parser

from influxdb import InfluxDBClient
from influxdb.resultset import ResultSet

from coinrat.domain import Balance
from coinrat.domain.portfolio import PortfolioSnapshotStorage, PortfolioSnapshot

PORTFOLIO_SNAPSHOT_STORAGE_NAME = 'influx_db'
PORTFOLIO_SNAPSHOT_MEASUREMENT_NAME = 'portfolio_snapshots'


class InvalidDataForOrderError(Exception):
    pass


class PortfolioSnapshotInnoDbStorage(PortfolioSnapshotStorage):
    def __init__(self, influx_db_client: InfluxDBClient) -> None:
        self._client = influx_db_client

    @property
    def name(self) -> str:
        return PORTFOLIO_SNAPSHOT_STORAGE_NAME

    def get_for_order(self, order_id: UUID) -> PortfolioSnapshot:
        sql = '''
            SELECT * FROM "{}" WHERE order_id ='{}'
        '''.format(PORTFOLIO_SNAPSHOT_MEASUREMENT_NAME, order_id)
        result: ResultSet = self._client.query(sql)
        data = list(result.get_points())
        if len(data) != 1:
            raise InvalidDataForOrderError(
                'Number of snapshots for order {} is {}. Exactly one needed.'.format(order_id, len(data))
            )

        return self._create_platform_snapshot_from_serialized(data[0])

    def get_for_strategy_run(self, strategy_run_id: UUID) -> Dict[str, PortfolioSnapshot]:
        sql = '''
            SELECT * FROM "{}" WHERE strategy_run_id ='{}'
        '''.format(PORTFOLIO_SNAPSHOT_MEASUREMENT_NAME, str(strategy_run_id))
        result: ResultSet = self._client.query(sql)
        data = list(result.get_points())

        result_data = {}

        for row in data:
            snapshot = self._create_platform_snapshot_from_serialized(row)
            result_data[str(snapshot.order_id)] = snapshot

        return result_data

    def save(self, portfolio_snapshot: PortfolioSnapshot) -> None:
        self._client.write_points([self._get_serialized_snapshot(portfolio_snapshot)])

    @staticmethod
    def _get_serialized_snapshot(portfolio_snapshot: PortfolioSnapshot) -> Dict:
        serialized_balances: Dict[str, float] = {}
        for balance in portfolio_snapshot.balances:
            serialized_balances[balance.currency] = float(balance.available_amount)

        return {
            'measurement': PORTFOLIO_SNAPSHOT_MEASUREMENT_NAME,
            'tags': {
                'order_id': str(portfolio_snapshot.order_id),
                'strategy_run_id': str(portfolio_snapshot.strategy_run_id),
                'market_name': str(portfolio_snapshot.market_name),
            },
            'time': portfolio_snapshot.time.isoformat(),
            'fields': serialized_balances,
        }

    @staticmethod
    def _create_platform_snapshot_from_serialized(row: Dict) -> PortfolioSnapshot:
        balances: List[Balance] = []
        market_name = row['market_name']

        for key, value in row.items():
            if value is None:
                value = '0'

            if key not in ['order_id', 'time', 'strategy_run_id', 'market_name']:
                balances.append(Balance(market_name, key, Decimal(value)))

        time = dateutil.parser.parse(row['time']).replace(tzinfo=datetime.timezone.utc)

        return PortfolioSnapshot(time, market_name, UUID(row['order_id']), UUID(row['strategy_run_id']), balances)
