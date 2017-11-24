import pytest
from flexmock import flexmock

from coinrat_cryptocompare import synchronizer_plugin
from coinrat_cryptocompare.synchronizer import CryptocompareSynchronizer


def test_plugin():
    storage = flexmock()

    assert 'coinrat_cryptocompare' == synchronizer_plugin.get_name()
    assert ['cryptocompare'] == synchronizer_plugin.get_available_synchronizers()
    assert isinstance(synchronizer_plugin.get_synchronizer('cryptocompare', storage), CryptocompareSynchronizer)
    with pytest.raises(ValueError):
        synchronizer_plugin.get_synchronizer('gandalf', storage)
