import logging

import datetime
import dateutil.parser
import click
import sys
import eventlet.wsgi
import os
import socketio

from flask import Flask
from logging.handlers import RotatingFileHandler
from typing import Tuple
from os.path import join, dirname

from click import Context
from dotenv import load_dotenv

from .server.server_factory import create_socket_io
from .domain import CurrentUtcDateTimeFactory
from .order_storage_plugins import OrderStoragePlugins
from .market_plugins import MarketPlugins
from .candle_storage_plugins import CandleStoragePlugins
from .synchronizer_plugins import SynchronizerPlugins
from .strategy_plugins import StrategyPlugins
from .domain import Pair, ForEndUserException, DateTimeInterval
from .domain.candle import CandleExporter
from .domain.order import OrderExporter

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# Todo: solve proper logging configuration
# logs_file = join(dirname(__file__), '../logs/log.log')
# logger = logging.getLogger()
# logger.addHandler(RotatingFileHandler(logs_file, maxBytes=200000, backupCount=5))
# logger.setLevel(logging.INFO)

candle_storage_plugins = CandleStoragePlugins()
order_storage_plugins = OrderStoragePlugins()
market_plugins = MarketPlugins()
synchronizer_plugins = SynchronizerPlugins()
strategy_plugins = StrategyPlugins()


@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.obj['influxdb_candle_storage'] = candle_storage_plugins.get_candle_storage('influx_db')
    ctx.obj['influxdb_order_storage'] = order_storage_plugins.get_order_storage('influx_db')


@cli.command(help='Shows available markets.')
def markets() -> None:
    click.echo('Available markers:')
    for market_name in market_plugins.get_available_markets():
        click.echo('  - {}'.format(market_name))


@cli.command(help='Shows available synchronizers.')
def synchronizers() -> None:
    click.echo('Available synchronizers:')
    for synchronizer_name in synchronizer_plugins.get_available_synchronizers():
        click.echo('  - {}'.format(synchronizer_name))


@cli.command(help="""
Exports candles into JSON file. Interval must be in UTC. \n\nExample: \n\n
    "python -m coinrat export_candles bittrex USD BTC \'2017-12-02T00:00:00\' \'2017-12-03T00:00:00\' output.json"
""")
@click.argument('market_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('interval', nargs=2)
@click.argument('output_file', nargs=1)
@click.pass_context
def export_candles(
    ctx: Context,
    market_name,
    pair: Tuple[str, str],
    interval: Tuple[str, str],
    output_file: str
) -> None:
    storage = ctx.obj['influxdb_candle_storage']
    pair = Pair(pair[0], pair[1])
    interval = DateTimeInterval(
        dateutil.parser.parse(interval[0]).replace(tzinfo=datetime.timezone.utc),
        dateutil.parser.parse(interval[1]).replace(tzinfo=datetime.timezone.utc)
    )
    exporter = CandleExporter(storage)
    exporter.export_to_file(output_file, market_name, pair, interval)


@cli.command(help="""
Exports orders into JSON file. Interval must be in UTC.

Example:
    "python -m coinrat export_orders bittrex USD BTC \'2017-12-02T00:00:00\' \'2017-12-03T00:00:00\' output.json"
""")
@click.argument('market_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('interval', nargs=2)
@click.argument('output_file', nargs=1)
@click.pass_context
def export_orders(
    ctx: Context,
    market_name,
    pair: Tuple[str, str],
    interval: Tuple[str, str],
    output_file: str
) -> None:
    storage = ctx.obj['influxdb_candle_storage']
    pair = Pair(pair[0], pair[1])
    interval = DateTimeInterval(
        dateutil.parser.parse(interval[0]).replace(tzinfo=datetime.timezone.utc),
        dateutil.parser.parse(interval[1]).replace(tzinfo=datetime.timezone.utc)
    )
    exporter = OrderExporter(storage)
    exporter.export_to_file(output_file, market_name, pair, interval)


@cli.command(help="""
Runs synchronization process. Synchronizes data from market into local database for analysis and strategies.

Example:
    python -m coinrat synchronize cryptocompare USD BTC
""")
@click.argument('synchronizer_name', nargs=1)
@click.argument('pair', nargs=2)
@click.pass_context
def synchronize(ctx: Context, synchronizer_name: str, pair: Tuple[str, str]) -> None:
    pair = Pair(pair[0], pair[1])

    synchronizer = synchronizer_plugins.get_synchronizer(synchronizer_name, ctx.obj['influxdb_candle_storage'])
    synchronizer.synchronize(pair)


@cli.command(help="""
Starts trading with given strategy.

Example:
    python -m coinrat run_strategy double_crossover bittrex
""")
@click.argument('strategy_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('market_names', nargs=-1)
@click.pass_context
def run_strategy(ctx: Context, strategy_name: str, pair: Tuple[str, str], market_names: Tuple[str]) -> None:
    pair = Pair(pair[0], pair[1])

    strategy = strategy_plugins.get_strategy(
        strategy_name,
        ctx.obj['influxdb_candle_storage'],
        ctx.obj['influxdb_order_storage'],
    )

    try:
        markers = [market_plugins.get_market(marker_name) for marker_name in market_names]
        strategy.run(markers, pair)
    except ForEndUserException as e:
        click.echo('ERROR: {}'.format(e), err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def testing(ctx: Context) -> None:  # Todo: Used only for testing during development, remove it after
    pair = Pair('USD', 'BTC')
    market = market_plugins.get_market('bittrex')
    print(market.get_pair_market_info(pair))


@cli.command(help="Starts an socket server for communication with frontend.")
@click.pass_context
def start_server(ctx: Context):
    storage = ctx.obj['influxdb_candle_storage']

    socket_io = create_socket_io(CurrentUtcDateTimeFactory(), storage)
    app = socketio.Middleware(socket_io, Flask(__name__))
    eventlet.wsgi.server(eventlet.listen((
        os.environ.get('SOCKET_SERVER_HOST'),
        int(os.environ.get('SOCKET_SERVER_PORT')),
    )), app)


def main():
    cli(obj={})
