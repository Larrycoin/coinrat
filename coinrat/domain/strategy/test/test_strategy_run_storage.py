import MySQLdb
import pytest
import os

current_directory = os.path.dirname(__file__)


@pytest.fixture
def mysql_connection_cursor():
    mysql_connection: MySQLdb.Connection = MySQLdb.connect(
        host='localhost',
        database='coinrat_test',
        user='root',
        password='root',
    )
    cursor = mysql_connection.cursor()
    cursor.execute('CREATE DATABASE `coinrat_test`')

    with open(os.path.join(current_directory, '/../../../../db/2018-01-27_142614_create_strategy_run.sql')) as f:
        read_data = f.read()

    yield cursor
    cursor.execute('DROP DATABASE `coinrat_test`')
