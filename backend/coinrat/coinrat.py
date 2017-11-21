import logging
import os
from os.path import join, dirname
from typing import Tuple

import click
import sys
from click import Context
from dotenv import load_dotenv

from coinrat_market import MarketPair
from coinrat_market_bittrex import bittrex_market_factory
from market_storage import market_storage_factory
from .market_synchronizer import MarketSynchronizer

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)


@click.group('coinrat')
@click.version_option(version='0.1')
@click.help_option()
@click.pass_context
def cli(ctx: Context) -> None:
    ctx.obj['market_storage'] = market_storage_factory('coinrat')


@cli.command()
@click.argument('market', nargs=1)
@click.argument('pair', nargs=2)
@click.pass_context
def synchronize(ctx: Context, market: str, pair: Tuple[str, str]) -> None:
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    if market == 'bittrex':
        bitrex_market = bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
        synchronizer = MarketSynchronizer(ctx.obj['market_storage'], bitrex_market)
        synchronizer.run(MarketPair(pair[0], pair[1]))

    else:
        raise Exception('Unknown market {}, not supported'.format(market))


def main():
    cli(obj={})
