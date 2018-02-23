from typing import Callable


class ThreadWatcher:
    def __init__(self, on_exception: Callable) -> None:
        super().__init__()
        self.on_exception = on_exception

    def notify_exception(self, exception: Exception):
        self.on_exception(exception)
