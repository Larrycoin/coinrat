from typing import List, Dict

from .coinrat import ForEndUserException
from .market import Market
from .pair import Pair


class StrategyConfigurationException(ForEndUserException):
    pass


class Strategy:
    def run(self, markets: List[Market], pair: Pair) -> None:
        raise NotImplementedError()

    def tick(self, markets: List[Market], pair: Pair) -> None:
        raise NotImplementedError()

    @staticmethod
    def get_configuration_structure() -> Dict:
        raise NotImplementedError()
