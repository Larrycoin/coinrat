import pytest
from flexmock import flexmock

from coinrat_double_crossover_strategy import strategy_plugin
from coinrat_double_crossover_strategy.strategy import DoubleCrossoverStrategy


def test_plugin():
    storage = flexmock()

    assert 'coinrat_double_crossover_strategy' == strategy_plugin.get_name()
    assert ['double_crossover'] == strategy_plugin.get_available_strategies()
    assert isinstance(strategy_plugin.get_strategy('double_crossover', storage), DoubleCrossoverStrategy)
    with pytest.raises(ValueError):
        strategy_plugin.get_strategy('gandalf', storage)
