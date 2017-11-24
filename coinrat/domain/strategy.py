from typing import List

from .coinrat import ForEndUserException
from .market import Market


class StrategyConfigurationException(ForEndUserException):
    pass


class Strategy:
    def run(self, markets: List[Market]) -> None:
        raise NotImplementedError()
