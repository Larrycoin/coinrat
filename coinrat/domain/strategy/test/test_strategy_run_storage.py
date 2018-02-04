import datetime
import MySQLdb
import pytest
import os
from uuid import UUID

from coinrat.db_migrations import run_db_migrations
from coinrat.domain import DateTimeInterval
from coinrat.domain.pair import Pair
from coinrat.domain.strategy import StrategyRunStorage, StrategyRun, StrategyRunMarket

current_directory = os.path.dirname(__file__)

DUMMY_DATE = datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc)


@pytest.fixture
def mysql_connection():
    database_name = os.environ.get('MYSQL_DATABASE') + '_test'
    connection: MySQLdb.Connection = MySQLdb.connect(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
    )
    cursor = connection.cursor()
    cursor.execute('CREATE DATABASE IF NOT EXISTS `{}`'.format(database_name))
    connection.select_db(database_name)
    run_db_migrations(connection, tag='coinrat_test')
    yield connection
    cursor.execute('DROP DATABASE `{}`'.format(database_name))


def test_save_strategy_run_and_find_it(mysql_connection: MySQLdb.Connection) -> None:
    storage = StrategyRunStorage(mysql_connection)
    strategy_run_to_save = StrategyRun(
        UUID('637f46a2-d008-48ba-9899-322abb56b425'),
        DUMMY_DATE,
        Pair('USD', 'BTC'),
        [StrategyRunMarket('yolo_market', 'yolo_plugin_name', {'foo': 'BAR'})],
        'strategy_dummy_name',
        {'gandalf': 'Gandalf the Gray'},
        DateTimeInterval(DUMMY_DATE, None),
        'candle_dummy_storage',
        'order_dummy_storage'
    )
    storage.insert(strategy_run_to_save)
    strategy_runs = storage.find_by()
    assert len(strategy_runs) == 1
    assert str(strategy_runs[0].strategy_run_id) == str(strategy_run_to_save.strategy_run_id)
