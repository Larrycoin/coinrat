import datetime
from typing import Union


class DateTimeInterval:
    def __init__(
        self,
        since: Union[datetime.datetime, None] = None,
        till: Union[datetime.datetime, None] = None
    ) -> None:
        assert since is None or '+00:00' in since.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(since.isoformat()))
        assert till is None or '+00:00' in till.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(till.isoformat()))

        self._since = since
        self._till = till

    @property
    def since(self) -> Union[datetime.datetime, None]:
        """None means unlimited."""
        return self._since

    @property
    def till(self) -> Union[datetime.datetime, None]:
        """None means unlimited."""
        return self._till
