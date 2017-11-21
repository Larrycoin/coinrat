import logging
from os.path import join, dirname
from typing import Tuple

import click
import sys
from click import Context
from dotenv import load_dotenv

from coinrat.market import MarketPair
from coinrat.synchronizer_factory import create_synchronizer
from coinrat_influx_db_storage import market_storage_factory

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


def main():
    cli(obj={})
