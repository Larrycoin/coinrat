class DiContainer:
    """Simple Dependency Injection Container that supports Lazy Loading"""

    def __init__(self) -> None:
        self._storage = {}

    def _get(self, name: str):
        if self._storage[name]['instance'] is None:
            self._storage[name]['instance'] = self.create_service(name)

        return self._storage[name]['instance']

    def create_service(self, name: str) -> object:
        return self._storage[name]['factory']()
