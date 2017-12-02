import datetime


class DateTimeFactory:
    def now(self) -> datetime.datetime:
        raise NotImplemented()


class CurrentUtcDateTimeFactory(DateTimeFactory):
    def now(self) -> datetime.datetime:
        return datetime.datetime.now().astimezone(datetime.timezone.utc)


class FrozenDateTimeFactory(DateTimeFactory):
    def __init__(self, freezed_at: datetime.datetime) -> None:
        self._freezed_at = freezed_at

    def now(self) -> datetime.datetime:
        return self._freezed_at

    def refreeze(self, freezed_at: datetime.datetime) -> None:
        self._freezed_at = freezed_at

    def move(self, delta: datetime.timedelta):
        self._freezed_at = self._freezed_at + delta
