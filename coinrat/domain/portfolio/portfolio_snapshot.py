import datetime

from typing import List, Dict
from uuid import UUID

from coinrat.domain import Balance, serialize_balances


class PortfolioSnapshot:
    def __init__(
        self,
        time: datetime.datetime,
        market_name: str,
        order_id: UUID,
        strategy_run_id: UUID,
        balances: List[Balance]
    ) -> None:
        self._time = time
        self._market_name = market_name
        self._strategy_run_id = strategy_run_id
        self._order_id = order_id
        self._balances = balances

    @property
    def time(self) -> datetime.datetime:
        return self._time

    @property
    def order_id(self) -> UUID:
        return self._order_id

    @property
    def strategy_run_id(self) -> UUID:
        return self._strategy_run_id

    @property
    def market_name(self) -> str:
        return self._market_name

    @property
    def balances(self) -> List[Balance]:
        return self._balances


def serialize_portfolio_snapshot(portfolio_snapshot: PortfolioSnapshot) -> Dict:
    return {
        'time': portfolio_snapshot.time.isoformat(),
        'order_id': str(portfolio_snapshot.order_id),
        'strategy_run_id': str(portfolio_snapshot.strategy_run_id),
        'market_name': portfolio_snapshot.market_name,
        'balances': serialize_balances(portfolio_snapshot.balances),
    }
