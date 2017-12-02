import datetime
import json

import os
from flexmock import flexmock
from decimal import Decimal

from coinrat.domain.candle import CandleExporter, MinuteCandle
from coinrat.domain import Pair


def test_candle_export():
    pair = Pair('USD', 'BTC')
    candle = MinuteCandle(
        'dummy_market',
        pair,
        datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        Decimal(1000),
        Decimal(2000),
        Decimal(3000),
        Decimal(4000)
    )

    storage = flexmock()
    storage.should_receive('find_by').and_return([candle])
    exporter = CandleExporter(storage)

    filepath = os.path.realpath(__file__) + '_orders.json'

    exporter.export_to_file(filepath, 'dummy_market', pair)

    expected = [{
        'market': 'dummy_market',
        'pair': 'USD_BTC',
        'time': '2017-01-01T00:00:00+00:00',
        'open': 1000.0,
        'close': 4000.0,
        'low': 3000.0,
        'high': 2000.0
    }]

    with open(filepath) as json_file:
        assert json.load(json_file) == expected

    os.remove(filepath)
