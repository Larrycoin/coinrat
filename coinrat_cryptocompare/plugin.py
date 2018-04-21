import pluggy
import requests

from coinrat.synchronizer_plugins import SynchronizerPluginSpecification
from .synchronizer import CryptocompareSynchronizer, SYNCHRONIZER_NAME

get_name_impl = pluggy.HookimplMarker('synchronizer_plugins')
get_available_synchronizers_spec = pluggy.HookimplMarker('synchronizer_plugins')
get_synchronizer_impl = pluggy.HookimplMarker('synchronizer_plugins')

PACKAGE_NAME = 'coinrat_cryptocompare'


class SynchronizerPlugin(SynchronizerPluginSpecification):
    @get_name_impl
    def get_name(self):
        return PACKAGE_NAME

    @get_available_synchronizers_spec
    def get_available_synchronizers(self):
        return [SYNCHRONIZER_NAME]

    @get_synchronizer_impl
    def get_synchronizer(self, synchronizer_name, storage, event_emitter):
        if synchronizer_name == SYNCHRONIZER_NAME:
            return CryptocompareSynchronizer(storage, event_emitter, requests.session())

        raise ValueError('Synchronizer "{}" not supported by this plugin.'.format(synchronizer_name))


synchronizer_plugin = SynchronizerPlugin()
