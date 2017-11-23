import logging
import click
import sys
from typing import Tuple
from os.path import join, dirname

from click import Context
from dotenv import load_dotenv

from .market_plugins import MarketPlugins, MarketNotProvidedByAnyPluginException
from .storage_plugins import StoragePlugins
from .synchronizer_plugins import SynchronizerPlugins
from .strategy_plugins import StrategyPlugins
from .domain import MarketPair, StrategyConfigurationException

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

storage_plugins = StoragePlugins()
market_plugins = MarketPlugins()
synchronizer_plugins = SynchronizerPlugins()
strategy_plugins = StrategyPlugins()


# Todo: write helps for click commands

@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.obj['market_inno_db_storage'] = storage_plugins.get_storage('influx_db')


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
@click.argument('synchronizer_name', nargs=1)
@click.argument('pair', nargs=2)
@click.pass_context
def synchronize(ctx: Context, synchronizer_name: str, pair: Tuple[str, str]) -> None:
    pair = MarketPair(pair[0], pair[1])

    synchronizer = synchronizer_plugins.get_synchronizer(synchronizer_name, ctx.obj['market_inno_db_storage'])
    synchronizer.synchronize(pair)


@cli.command()
@click.argument('strategy_name', nargs=1)
@click.argument('market_names', nargs=-1)
@click.pass_context
def run_strategy(ctx: Context, strategy_name: str, market_names: Tuple[str]) -> None:
    strategy = strategy_plugins.get_strategy(strategy_name, ctx.obj['market_inno_db_storage'])

    try:
        markers = [market_plugins.get_market(marker_name) for marker_name in market_names]
    except (MarketNotProvidedByAnyPluginException, StrategyConfigurationException) as e:
        click.echo(e, err=True)
        sys.exit(1)

    strategy.run(markers)


def main():
    cli(obj={})
