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

        self._since: Union[datetime.datetime, None] = since
        self._till: Union[datetime.datetime, None] = till

    @property
    def since(self) -> Union[datetime.datetime, None]:
        """None means unlimited."""
        return self._since

    @property
    def till(self) -> Union[datetime.datetime, None]:
        """None means unlimited."""
        return self._till

    def contains(self, date_time: datetime.datetime):
        assert '+00:00' in date_time.isoformat()[-6:], \
            ('Time must be in UTC and aware of its timezone ({})'.format(date_time.isoformat()))

        return (self._since is None or self._since < date_time) and (self._till is None or self._till > date_time)

    def __str__(self):
        return '[{}, {}]'.format(
            'None' if self._since is None else self._since.isoformat(),
            'None' if self._till is None else self._till.isoformat()
        )
