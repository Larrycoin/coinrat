import logging

import datetime
import dateutil.parser
import click
import sys

from logging.handlers import RotatingFileHandler
from typing import Tuple
from os.path import join, dirname

from click import Context
from dotenv import load_dotenv

from .order_storage_plugins import OrderStoragePlugins
from .market_plugins import MarketPlugins
from .candle_storage_plugins import CandleStoragePlugins
from .synchronizer_plugins import SynchronizerPlugins
from .strategy_plugins import StrategyPlugins
from .domain import Pair, ForEndUserException
from .domain.candle import CandleExporter

dotenv_path = join(dirname(__file__), '../.env')
load_dotenv(dotenv_path)

# Todo: solve proper logging configuration
logs_file = join(dirname(__file__), '../logs/log.log')
logger = logging.getLogger()
logger.addHandler(RotatingFileHandler(logs_file, maxBytes=200000, backupCount=5))
logger.setLevel(logging.INFO)

candle_storage_plugins = CandleStoragePlugins()
order_storage_plugins = OrderStoragePlugins()
market_plugins = MarketPlugins()
synchronizer_plugins = SynchronizerPlugins()
strategy_plugins = StrategyPlugins()


# Todo: write helps for click commands

@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.obj['influxdb_candle_storage'] = candle_storage_plugins.get_candle_storage('influx_db')
    ctx.obj['influxdb_order_storage'] = order_storage_plugins.get_order_storage('influx_db')


@cli.command()
def markets() -> None:
    click.echo('Available markers:')
    for market_name in market_plugins.get_available_markets():
        click.echo('  - {}'.format(market_name))


@cli.command()
def synchronizers() -> None:
    click.echo('Available synchronizers:')
    for synchronizer_name in synchronizer_plugins.get_available_synchronizers():
        click.echo('  - {}'.format(synchronizer_name))


@cli.command()
@click.argument('market_name', nargs=1)
@click.argument('pair', nargs=2)
@click.argument('interval', nargs=2)  # todo: document that in utc
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
    since = dateutil.parser.parse(interval[0]).replace(tzinfo=datetime.timezone.utc)
    till = dateutil.parser.parse(interval[1]).replace(tzinfo=datetime.timezone.utc)
    exporter = CandleExporter(storage)
    exporter.export_to_file(output_file, market_name, pair, since, till)


@cli.command()
@click.argument('synchronizer_name', nargs=1)
@click.argument('pair', nargs=2)
@click.pass_context
def synchronize(ctx: Context, synchronizer_name: str, pair: Tuple[str, str]) -> None:
    pair = Pair(pair[0], pair[1])

    synchronizer = synchronizer_plugins.get_synchronizer(synchronizer_name, ctx.obj['influxdb_candle_storage'])
    synchronizer.synchronize(pair)


@cli.command()
@click.argument('strategy_name', nargs=1)
@click.argument('market_names', nargs=-1)
@click.pass_context
def run_strategy(ctx: Context, strategy_name: str, market_names: Tuple[str]) -> None:
    strategy = strategy_plugins.get_strategy(
        strategy_name,
        ctx.obj['influxdb_candle_storage'],
        ctx.obj['influxdb_order_storage'],
    )

    try:
        markers = [market_plugins.get_market(marker_name) for marker_name in market_names]
        strategy.run(markers)
    except ForEndUserException as e:
        click.echo('ERROR: {}'.format(e), err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def testing(ctx: Context) -> None:  # Todo: Used only for testing during development, remove it after
    pair = Pair('USD', 'BTC')
    market = market_plugins.get_market('bittrex')
    print(market.get_pair_market_info(pair))


def main():
    cli(obj={})
