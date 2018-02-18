from typing import Set

import pluggy

get_name_spec = pluggy.HookspecMarker('coinrat_plugins')
get_description_spec = pluggy.HookspecMarker('coinrat_plugins')


class PluginSpecification:
    @get_name_spec
    def get_name(self):
        raise NotImplementedError()

    @get_description_spec
    def get_description(self):
        raise NotImplementedError()


def plugins_loader(entry_points_name: str, plugin_specification) -> Set[PluginSpecification]:
    manager = pluggy.PluginManager('coinrat_plugins')
    manager.add_hookspecs(plugin_specification)
    manager.load_setuptools_entrypoints(entry_points_name)
    manager.check_pending()
    return manager.get_plugins()
