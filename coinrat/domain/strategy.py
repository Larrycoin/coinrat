from typing import List, Dict

from .coinrat import ForEndUserException
from .market import Market
from .pair import Pair


class StrategyConfigurationException(ForEndUserException):
    pass


class Strategy:
    def tick(self, markets: List[Market], pair: Pair) -> None:
        raise NotImplementedError()

    def get_seconds_delay_between_runs(self) -> float:
        raise NotImplementedError()

    @staticmethod
    def get_configuration_structure() -> Dict[str, str]:
        raise NotImplementedError()
