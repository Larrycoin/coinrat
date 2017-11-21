import os
from os.path import join, dirname
from dotenv import load_dotenv

from coinrat_bittrex import bittrex_market_factory, MARKET_BITTREX
from coinrat_market import MarketPair
from market_storage import market_storage_factory

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bitrex_market = bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
# print(bitrex_market.sell_max_available(MarketPair('USDT', 'BTC')))

market_storage = market_storage_factory('coinrat')
candles = bitrex_market.get_candles(MarketPair('USDT', 'BTC'))
market_storage.write_candles(MARKET_BITTREX, candles)
