import datetime

from coinrat.domain import DateTimeInterval


def test_immutability():
    date0 = datetime.datetime(2017, 12, 31, 0, 0, 0, tzinfo=datetime.timezone.utc)
    date1 = datetime.datetime(2018, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc)
    date2 = datetime.datetime(2018, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
    date3 = datetime.datetime(2018, 1, 3, 0, 0, 0, tzinfo=datetime.timezone.utc)

    interval = DateTimeInterval(date1, date2)
    assert str(interval) == '[2018-01-01T00:00:00+00:00, 2018-01-02T00:00:00+00:00]'

    new_till_interval = interval.with_till(date3)
    assert str(new_till_interval) == '[2018-01-01T00:00:00+00:00, 2018-01-03T00:00:00+00:00]'
    assert interval != new_till_interval

    new_since_interval = interval.with_since(date0)
    assert str(new_since_interval) == '[2017-12-31T00:00:00+00:00, 2018-01-02T00:00:00+00:00]'
    assert interval != new_since_interval
