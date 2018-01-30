from coinrat.domain.strategy import StrategyRunMarket, serialize_strategy_run_market


def test_serialize_strategy_run_market() -> None:
    strategy_run_market = StrategyRunMarket('yolo', {'A': 'AAA'})
    assert serialize_strategy_run_market(strategy_run_market) == {'configuration': {'A': 'AAA'}, 'name': 'yolo'}
