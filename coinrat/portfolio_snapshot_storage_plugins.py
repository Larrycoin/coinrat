import pluggy
from typing import List, Set, cast

from .plugins import PluginSpecification, plugins_loader
from .domain.portfolio import PortfolioSnapshotStorage

get_available_portfolio_snapshot_storages_spec = pluggy.HookspecMarker('coinrat_plugins')
get_portfolio_snapshot_storage_spec = pluggy.HookspecMarker('coinrat_plugins')


#   "ValueError: Function has keyword-only parameters or annotations, use getfullargspec() API which can support them"
class PortfolioSnapshotStoragePluginSpecification(PluginSpecification):
    @get_available_portfolio_snapshot_storages_spec
    def get_available_portfolio_snapshot_storages(self):
        pass

    @get_portfolio_snapshot_storage_spec
    def get_portfolio_snapshot_storage(self, name):
        pass


class PortfolioSnapshotStorageNotProvidedByAnyPluginException(Exception):
    pass


class PortfolioSnapshotStoragePlugins:
    def __init__(self) -> None:
        self._plugins = cast(
            Set[PortfolioSnapshotStoragePluginSpecification],
            plugins_loader('coinrat_portfolio_snapshot_storage_plugins', PortfolioSnapshotStoragePluginSpecification)
        )

    def get_available_portfolio_snapshot_storages(self) -> List[str]:
        return [
            storage_name for plugin in self._plugins \
            for storage_name in plugin.get_available_portfolio_snapshot_storages()
        ]

    def get_portfolio_snapshot_storage(self, name: str) -> PortfolioSnapshotStorage:
        for plugin in self._plugins:
            if name in plugin.get_available_portfolio_snapshot_storages():
                return plugin.get_portfolio_snapshot_storage(name)

        raise PortfolioSnapshotStorageNotProvidedByAnyPluginException(
            'PortfolioSnapshot storage "{}" not found.'.format(name)
        )
