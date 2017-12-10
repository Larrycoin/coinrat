import datetime
import dateutil.parser

from typing import Dict

from coinrat.domain import DateTimeInterval


def parse_interval(data: Dict[str, str]) -> DateTimeInterval:
    since = data['since']
    till = data['till']

    return DateTimeInterval(
        dateutil.parser.parse(since).replace(tzinfo=datetime.timezone.utc) if since is not None else None,
        dateutil.parser.parse(till).replace(tzinfo=datetime.timezone.utc) if till is not None else None
    )
