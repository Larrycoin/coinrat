from uuid import UUID

import datetime
import pytest
from decimal import Decimal
from influxdb import InfluxDBClient

from coinrat.domain import Balance
from coinrat.domain.pair import Pair
from coinrat.domain.portfolio import PortfolioSnapshot
from coinrat_influx_db_storage.portfolio_snapshot_storage import PortfolioSnapshotInnoDbStorage

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_ORDER_ID = UUID('16fd2706-8baf-433b-82eb-8c7fada847db')
STRATEGY_RUN_ID = UUID('99fd2706-8baf-433b-82eb-8c7fada847ff')
DUMMY_TIME = datetime.datetime(2017, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)


@pytest.fixture
def influx_database():
    influx = InfluxDBClient()
    influx.create_database('coinrat_test')
    influx._database = 'coinrat_test'
    yield influx
    influx.drop_database('coinrat_test')


def test_save_and_load_portfolio_storage_in_influxdb(influx_database: InfluxDBClient):
    storage = PortfolioSnapshotInnoDbStorage(influx_database)
    storage.save(
        PortfolioSnapshot(
            DUMMY_TIME,
            DUMMY_MARKET,
            DUMMY_ORDER_ID,
            STRATEGY_RUN_ID,
            [
                Balance(DUMMY_MARKET, 'USD', Decimal('500')),
                Balance(DUMMY_MARKET, 'BTC', Decimal('0.5')),
            ]
        )
    )

    result = storage.get_for_order(DUMMY_ORDER_ID)
    assert isinstance(result, PortfolioSnapshot)
    assert DUMMY_ORDER_ID == result.order_id
    assert 2 == len(result.balances)

    assert 'USD' in list(map(lambda balance: balance.currency, result.balances))
    assert 'BTC' in list(map(lambda balance: balance.currency, result.balances))

    assert Decimal('500') in list(map(lambda balance: balance.available_amount, result.balances))
    assert Decimal('0.5') in list(map(lambda balance: balance.available_amount, result.balances))

    snapshots = storage.get_for_strategy_run(STRATEGY_RUN_ID)
    assert isinstance(snapshots[str(DUMMY_ORDER_ID)], PortfolioSnapshot)
