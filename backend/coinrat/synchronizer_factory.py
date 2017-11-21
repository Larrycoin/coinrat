import os

import requests

from coinrat.market import MarketStateSynchronizer, MarketStorage
from coinrat_bittrex import bittrex_market_factory, BittrexSynchronizer
from coinrat_cryptocompare import CryptocompareSynchronizer


def create_synchronizer(market_name: str, storage: MarketStorage) -> MarketStateSynchronizer:
    if market_name == 'bittrex':
        bitrex_market = bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
        return BittrexSynchronizer(bitrex_market, storage)

    elif market_name.startswith('cryptocompare'):
        return CryptocompareSynchronizer(market_name.split('-')[1], storage, requests.Session())

    else:
        raise Exception('Unknown market {}, not supported'.format(market_name))
