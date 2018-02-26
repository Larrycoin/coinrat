from uuid import UUID

import datetime
from decimal import Decimal

from coinrat.domain import Balance
from coinrat.domain.pair import Pair
from coinrat.domain.portfolio import PortfolioSnapshot, serialize_portfolio_snapshot

DUMMY_MARKET = 'dummy_market'
BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_ORDER_ID = UUID('16fd2706-8baf-433b-82eb-8c7fada847db')
STRATEGY_RUN_ID = UUID('99fd2706-8baf-433b-82eb-8c7fada847ff')
DUMMY_TIME = datetime.datetime(2017, 1, 2, 3, 4, 5, tzinfo=datetime.timezone.utc)


def test_serialize_portfolio_snapshot():
    snapshot = PortfolioSnapshot(
        DUMMY_TIME,
        DUMMY_MARKET,
        DUMMY_ORDER_ID,
        STRATEGY_RUN_ID,
        [
            Balance(DUMMY_MARKET, 'USD', Decimal('500')),
            Balance(DUMMY_MARKET, 'BTC', Decimal('0.5')),
        ]
    )

    assert {
               'balances': [
                   {'available_amount': '500', 'currency': 'USD'},
                   {'available_amount': '0.5', 'currency': 'BTC'}
               ],
               'market_name': 'dummy_market',
               'order_id': '16fd2706-8baf-433b-82eb-8c7fada847db',
               'strategy_run_id': '99fd2706-8baf-433b-82eb-8c7fada847ff',
               'time': '2017-01-02T03:04:05+00:00'
           } == serialize_portfolio_snapshot(snapshot)
