import os
from os.path import join, dirname

from decimal import Decimal
from dotenv import load_dotenv

from coinrat_bittrex import BittrexMarket
from coinrat_market import Order, MarketPair, ORDER_TYPE_MARKET, ORDER_TYPE_LIMIT

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

bitrex_market = BittrexMarket(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))
# print(bitrex_market.get_balance('BTC'))
# print(list(bitrex_market.get_candles('USDT-BTC')))

# order = Order(MarketPair('USDT', 'BTC'), ORDER_TYPE_LIMIT, Decimal('0.0005'), Decimal('8150'))
# print(bitrex_market.create_sell_order(order))

bitrex_market.cancel_order('c1266aff-0b35-4335-8afe-3c9ca580d8b2')
