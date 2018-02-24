from typing import List, Dict

from coinrat.domain.coinrat import ForEndUserException
from coinrat.domain.market import Market


class StrategyConfigurationException(ForEndUserException):
    pass


class Strategy:
    def tick(self, markets: List[Market]) -> None:
        raise NotImplementedError()

    def get_seconds_delay_between_ticks(self) -> float:
        raise NotImplementedError()

    @staticmethod
    def get_configuration_structure() -> Dict[str, Dict[str, str]]:
        raise NotImplementedError()
