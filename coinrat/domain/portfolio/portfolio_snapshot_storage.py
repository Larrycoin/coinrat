from typing import Dict
from uuid import UUID

from .portfolio_snapshot import PortfolioSnapshot


class PortfolioSnapshotStorage:
    def save(self, portfolio_snapshot: PortfolioSnapshot):
        raise NotImplementedError()

    def get_for_order(self, order_id: UUID) -> PortfolioSnapshot:
        raise NotImplementedError()

    def get_for_strategy_run(self, strategy_run_id: UUID) -> Dict[str, PortfolioSnapshot]:
        raise NotImplementedError()
