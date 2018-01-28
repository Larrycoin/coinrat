from coinrat.domain.strategy.strategy_run import StrategyRun


class StrategyRunner:
    def run(self, strategy_run: StrategyRun):
        raise NotImplementedError()
