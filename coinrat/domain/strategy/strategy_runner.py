from coinrat.domain.strategy.strategy_run import StrategyRun


class SkipTickException(Exception):
    pass


class StrategyRunner:
    def run(self, strategy_run: StrategyRun):
        raise NotImplementedError()
