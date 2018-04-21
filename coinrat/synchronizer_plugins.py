import pluggy
from typing import List, Set, cast

from coinrat.event.event_emitter import EventEmitter
from .plugins import PluginSpecification, plugins_loader
from .domain import MarketStateSynchronizer
from .domain.candle import CandleStorage

get_name_spec = pluggy.HookspecMarker('coinrat_plugins')

get_available_synchronizers_spec = pluggy.HookspecMarker('coinrat_plugins')
get_synchronizer_spec = pluggy.HookspecMarker('coinrat_plugins')


class SynchronizerPluginSpecification(PluginSpecification):
    @get_name_spec
    def get_name(self):
        raise NotImplementedError()

    @get_available_synchronizers_spec
    def get_available_synchronizers(self):
        raise NotImplementedError()

    @get_synchronizer_spec
    def get_synchronizer(self, synchronizer_name, storage, event_emitter):
        raise NotImplementedError()


class SynchronizerNotProvidedByAnyPluginException(Exception):
    pass


class SynchronizerPlugins:
    def __init__(self) -> None:
        self._plugins = cast(
            Set[SynchronizerPluginSpecification],
            plugins_loader('coinrat_synchronizer_plugins', SynchronizerPluginSpecification)
        )

    def get_available_synchronizers(self) -> List[str]:
        return [
            synchronize_name for plugin in self._plugins for synchronize_name in plugin.get_available_synchronizers()
        ]

    def get_synchronizer(
        self,
        synchronizer_name: str,
        storage: CandleStorage,
        event_emitter: EventEmitter
    ) -> MarketStateSynchronizer:
        for plugin in self._plugins:
            if synchronizer_name in plugin.get_available_synchronizers():
                return plugin.get_synchronizer(synchronizer_name, storage, event_emitter)

        raise SynchronizerNotProvidedByAnyPluginException('Synchronizer "{}" not found.'.format(synchronizer_name))
