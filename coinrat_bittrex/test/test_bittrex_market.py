import copy
import datetime
import pytest
import uuid
from decimal import Decimal
from typing import Dict, Union
from uuid import UUID

from flexmock import flexmock

from coinrat.domain import Pair, MarketOrderException
from coinrat.domain.order import Order, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, DIRECTION_BUY, DIRECTION_SELL, \
    NotEnoughBalanceToPerformOrderException
from coinrat_bittrex.market import BittrexMarket
from coinrat_bittrex.test.fixtures import MARKET_USDT_BTC_DATA, DUMMY_ORDER_ID_ON_MARKET, OPEN_ORDER, CLOSED_ORDER

BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_LIMIT_BUY_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    'bittrex',
    DIRECTION_BUY,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000)
)
DUMMY_MARKET_BUY_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
    'bittrex',
    DIRECTION_BUY,
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_MARKET,
    Decimal(1),
    None
)
MY_BTC_BALANCE = 100
MY_USD_BALANCE = 1000000

flexmock(uuid).should_receive('uuid4').and_return(UUID('16fd2706-8baf-433b-82eb-8c7fada847da'))


def test_get_balance():
    market = BittrexMarket(flexmock(), mock_client_v2())
    balance = market.get_balance('BTC')

    assert 'BTC' == balance.currency
    assert Decimal(MY_BTC_BALANCE) == balance.available_amount
    assert 'bittrex' == balance.market_name


def test_place_order():
    client_v1 = flexmock()
    client_v1 \
        .should_receive('sell_limit') \
        .with_args('USDT-BTC', 1, 8000) \
        .and_return({'success': True, 'result': {'uuid': 'abcd'}}) \
        .once()
    market = BittrexMarket(client_v1, mock_client_v2())

    order = copy.deepcopy(DUMMY_LIMIT_BUY_ORDER)
    order._direction = DIRECTION_SELL

    order = market.place_order(order)

    assert '16fd2706-8baf-433b-82eb-8c7fada847da' == str(order.order_id)
    assert 'abcd' == order.id_on_market


def test_market_order_not_implemented():
    market = BittrexMarket(flexmock(), mock_client_v2())

    with pytest.raises(NotImplementedError):
        market.place_order(DUMMY_MARKET_BUY_ORDER)


def test_invalid_order():
    market = BittrexMarket(flexmock(), mock_client_v2())

    order = copy.deepcopy(DUMMY_LIMIT_BUY_ORDER)
    order._type = 'gandalf'

    with pytest.raises(ValueError):
        market.place_order(order)


def test_not_enough_balance():
    order = copy.deepcopy(DUMMY_LIMIT_BUY_ORDER)
    order._quantity = Decimal(0.00001)

    market = BittrexMarket(flexmock(), mock_client_v2())
    with pytest.raises(NotEnoughBalanceToPerformOrderException):
        market.place_order(order)


def test_cancel_order():
    client_v1 = flexmock()
    client_v1.should_receive('cancel').with_args('abcd').and_return({'success': True}).once()

    market = BittrexMarket(client_v1, mock_client_v2())
    market.cancel_order('abcd')


@pytest.mark.parametrize(['expected_open', 'expected_closed_at', 'expected_quantity_amount', 'bittrex_response'],
    [
        (True, None, Decimal(0.00310976), OPEN_ORDER),
        (
            False,
            datetime.datetime(2017, 11, 26, 13, 8, 14, 497000, tzinfo=datetime.timezone.utc),
            Decimal(0),
            CLOSED_ORDER
        ),
    ]
)
def test_get_oder_status(
    expected_open: bool,
    expected_closed_at: Union[datetime.datetime, None],
    expected_quantity_amount: Decimal,
    bittrex_response: Dict
):
    client_v2 = flexmock()
    client_v2.should_receive('get_order').with_args(DUMMY_ORDER_ID_ON_MARKET).and_return(bittrex_response)

    market = BittrexMarket(flexmock(), client_v2)
    order = flexmock(id_on_market=DUMMY_ORDER_ID_ON_MARKET)
    order_status = market.get_order_status(order)

    assert expected_open == order_status.is_open
    assert expected_closed_at == order_status.closed_at
    assert expected_quantity_amount == order_status.quantity_remaining


def test_result_validation():
    BittrexMarket._validate_result({'success': True})

    with pytest.raises(MarketOrderException):
        BittrexMarket._validate_result({'success': False, 'message': 'You shall not pass!'})


def mock_client_v2():
    client_v2 = flexmock()
    client_v2.should_receive('get_markets').and_return({'success': True, 'result': [MARKET_USDT_BTC_DATA]})
    client_v2.should_receive('get_balance') \
        .with_args('BTC') \
        .and_return({'success': True, 'result': {'Available': str(MY_BTC_BALANCE)}})
    client_v2.should_receive('get_balance') \
        .with_args('USDT') \
        .and_return({'success': True, 'result': {'Available': str(MY_USD_BALANCE)}})
    client_v2.should_receive('get_candles').and_return({
        'success': True,
        'message': '',
        'result': [
            {
                'O': 80,
                'H': 110,
                'L': 90,
                'C': 105,
                'V': 14.96648765,
                'T': '2017-11-15T13:21:00',
                'BV': 106043.18764751,
            }
        ]
    })

    return client_v2
