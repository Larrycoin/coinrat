import os
import pluggy
from typing import Dict
from coinrat.domain import Plugin, Market, Strategy, MarketsCandleStorage

from .synchronizer import BittrexSynchronizer
from .market import bittrex_market_factory, MARKET_BITREX

name = pluggy.HookspecMarker('coinrat')
markets = pluggy.HookspecMarker('coinrat')
strategies = pluggy.HookspecMarker('coinrat')
storages = pluggy.HookspecMarker('coinrat')
synchronizers = pluggy.HookspecMarker('coinrat')


class CoinRatBittrexPlugin(Plugin):
    def __init__(self) -> None:
        self._market = bittrex_market_factory(os.environ.get('BITREX_KEY'), os.environ.get('BITREX_SECRET'))

    @name
    def get_name(self) -> str:
        return 'bittrex'

    @markets
    def get_markets(self) -> Dict[str, Market]:
        return {MARKET_BITREX: self._market}

    @strategies
    def get_strategies(self) -> Dict[str, Strategy]:
        pass

    @storages
    def get_storages(self) -> Dict[str, MarketsCandleStorage]:
        pass

    @synchronizers
    def get_synchronizers(self) -> Dict[str, MarketsCandleStorage]:
        return {BittrexSynchronizer(self._market, storage)}
