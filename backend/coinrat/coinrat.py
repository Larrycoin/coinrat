import datetime
import logging
from os.path import join, dirname
from typing import Tuple

import click
import sys
from click import Context
from dotenv import load_dotenv

from .double_crossover_strategy.strategy import DoubleCrossoverStrategy, DOUBLE_CROSSOVER_STRATEGY
from .domain import MarketPair
from .synchronizer_factory import create_synchronizer
from .coinrat_influx_db_storage import market_storage_factory

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.obj['market_inno_db_storage'] = market_storage_factory('coinrat')


@cli.command()
@click.argument('market_name', nargs=1)
@click.argument('pair', nargs=2)
@click.pass_context
def synchronize(ctx: Context, market_name: str, pair: Tuple[str, str]) -> None:
    pair = MarketPair(pair[0], pair[1])
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    synchronizer = create_synchronizer(market_name, ctx.obj['market_inno_db_storage'])
    synchronizer.synchronize(pair)


@cli.command()
@click.argument('strategy_name', nargs=1)
@click.argument('market_name', nargs=1)  # Todo: strategy in the future is not bound to one market
@click.argument('pair', nargs=2)  # Todo: strategy in the future is not bound to one pair
@click.pass_context
def run_strategy(ctx: Context, strategy_name: str, market_name: str, pair: Tuple[str, str]) -> None:
    pair = MarketPair(pair[0], pair[1])
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    if strategy_name == DOUBLE_CROSSOVER_STRATEGY:
        strategy = DoubleCrossoverStrategy(
            market_name,
            pair,
            ctx.obj['market_inno_db_storage'],
            datetime.timedelta(hours=1),
            datetime.timedelta(minutes=15)
        )
        strategy.run()

    else:
        raise ValueError('not supported')


def main():
    cli(obj={})
