import os
from os.path import join, dirname
from dotenv import load_dotenv

from coinrat_bittrex import BittrexMarket

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bitrex_market = BittrexMarket(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
print(bitrex_market.get_balance('BTC'))
print(list(bitrex_market.get_candles('USDT-BTC')))
