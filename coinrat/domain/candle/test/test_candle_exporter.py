import datetime
import json

import os
from flexmock import flexmock
from decimal import Decimal

from coinrat.domain.candle import CandleExporter, Candle
from coinrat.domain.pair import Pair


def test_candle_export_import():
    pair = Pair('USD', 'BTC')
    candle = Candle(
        'dummy_market',
        pair,
        datetime.datetime(2017, 1, 1, 0, 0, 0, tzinfo=datetime.timezone.utc),
        Decimal('1000'),
        Decimal('2000'),
        Decimal('3000'),
        Decimal('4000')
    )

    storage = flexmock()
    storage.should_receive('find_by').and_return([candle]).once()
    storage.should_receive('write_candles').once()
    exporter = CandleExporter(storage)
    file_name = os.path.dirname(__file__) + '_orders.json'

    exporter.export_to_file(file_name, 'dummy_market', pair)

    expected = [{
        'market': 'dummy_market',
        'pair': 'USD_BTC',
        'time': '2017-01-01T00:00:00+00:00',
        'open': "1000.00000000",
        'high': "2000.00000000",
        'low': "3000.00000000",
        'close': "4000.00000000",
        'size': '1-minute',
    }]

    with open(file_name) as json_file:
        assert json.load(json_file) == expected

    exporter.import_from_file(file_name)

    os.remove(file_name)
