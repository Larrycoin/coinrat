import pluggy
from typing import List, Set, cast

from .plugins import PluginSpecification, plugins_loader
from coinrat.domain.order import OrderStorage

get_available_order_storages_spec = pluggy.HookspecMarker('coinrat_plugins')
get_order_storage_spec = pluggy.HookspecMarker('coinrat_plugins')


#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class OrderStoragePluginSpecification(PluginSpecification):
    @get_available_order_storages_spec
    def get_available_order_storages(self):
        raise NotImplementedError()

    @get_order_storage_spec
    def get_order_storage(self, name):
        raise NotImplementedError()


class OrderStorageNotProvidedByAnyPluginException(Exception):
    pass


class OrderStoragePlugins:
    def __init__(self) -> None:
        self._plugins = cast(
            Set[OrderStoragePluginSpecification],
            plugins_loader('coinrat_order_storage_plugins',OrderStoragePluginSpecification)
        )

    def get_available_order_storages(self) -> List[str]:
        return [storage_name for plugin in self._plugins for storage_name in plugin.get_available_order_storages()]

    def get_order_storage(self, name: str) -> OrderStorage:
        for plugin in self._plugins:
            if name in plugin.get_available_order_storages():
                return plugin.get_order_storage(name)

        raise OrderStorageNotProvidedByAnyPluginException('Order storage "{}" not found.'.format(name))
