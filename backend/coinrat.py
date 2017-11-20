import os
from os.path import join, dirname
from dotenv import load_dotenv
from coinrat_bittrex import BittrexMarket
from coinrat_market import MarketPair

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bitrex_market = BittrexMarket(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
# print(bitrex_market.sell_max_available(MarketPair('USDT', 'BTC')))
