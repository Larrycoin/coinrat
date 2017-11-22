import logging
import click
import sys
from typing import Tuple, Set
from os.path import join, dirname

from click import Context
from dotenv import load_dotenv

from .synchronizer_plugins import SynchronizerPlugins
from .storage_plugins import StoragePlugins
from .domain import MarketPair

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

storage_plugins = StoragePlugins()
synchronizer_plugins = SynchronizerPlugins()


@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.obj['market_inno_db_storage'] = storage_plugins.get_storage('influx_db')


@cli.command()
@click.argument('synchronizer', nargs=1)
@click.argument('pair', nargs=2)
@click.pass_context
def synchronize(ctx: Context, synchronizer_name: str, pair: Tuple[str, str]) -> None:
    pair = MarketPair(pair[0], pair[1])

    synchronizer = synchronizer_plugins.get_synchronizer(synchronizer_name)
    synchronizer.synchronize(pair)


@cli.command()
@click.argument('strategy_name', nargs=1)
@click.argument('market_name', nargs=1)  # Todo: strategy in the future is not bound to one market
@click.argument('pair', nargs=2)  # Todo: strategy in the future is not bound to one pair
@click.pass_context
def run_strategy(ctx: Context, strategy_name: str, market_name: str, pair: Tuple[str, str]) -> None:
    pair = MarketPair(pair[0], pair[1])

    # if strategy_name == DOUBLE_CROSSOVER_STRATEGY:
    #     strategy = DoubleCrossoverStrategy(
    #         market_name,
    #         pair,
    #         ctx.obj['market_inno_db_storage'],
    #         datetime.timedelta(hours=1),
    #         datetime.timedelta(minutes=15)
    #     )
    #     strategy.run()
    #
    # else:
    #     raise ValueError('not supported')


def main():
    cli(obj={})
