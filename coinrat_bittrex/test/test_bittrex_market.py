import copy, pytest
import uuid
from decimal import Decimal
from uuid import UUID

import datetime
from flexmock import flexmock

from coinrat_bittrex.market import BittrexMarket, BittrexMarketRequestException
from coinrat.domain import Pair, Order, ORDER_TYPE_LIMIT, ORDER_TYPE_MARKET, \
    NotEnoughBalanceToPerformOrderException

BTC_USD_PAIR = Pair('USD', 'BTC')
DUMMY_LIMIT_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847da'),
    'bittrex',
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_LIMIT,
    Decimal(1),
    Decimal(8000)
)
DUMMY_MARKET_ORDER = Order(
    UUID('16fd2706-8baf-433b-82eb-8c7fada847db'),
    'bittrex',
    datetime.datetime(2017, 11, 26, 10, 11, 12, tzinfo=datetime.timezone.utc),
    BTC_USD_PAIR,
    ORDER_TYPE_MARKET,
    Decimal(1),
    None
)
MY_BTC_BALANCE = 100
MY_USD_BALANCE = 1000000

MARKET_USDT_BTC_DATA = {
    'MarketCurrency': 'BTC',
    'BaseCurrency': 'USDT',
    'MarketCurrencyLong': 'Bitcoin',
    'BaseCurrencyLong': 'Tether',
    'MinTradeSize': 0.00039117,
    'MarketName': 'USDT-BTC',
    'IsActive': True,
    'Created': '2015-12-11T06:31:40.633',
    'Notice': None,
    'IsSponsored': None,
    'LogoUrl': None
}

# Todo: rewrite do proper DI to be able mockID for each test separately
flexmock(uuid).should_receive('uuid4').and_return(UUID('16fd2706-8baf-433b-82eb-8c7fada847da'))


def test_get_balance():
    market = BittrexMarket(flexmock(), mock_client_v2())
    balance = market.get_balance('BTC')

    assert 'BTC' == balance.currency
    assert Decimal(MY_BTC_BALANCE) == balance.available_amount
    assert 'bittrex' == balance.market_name


def test_create_sell_order():
    client_v1 = flexmock()
    client_v1 \
        .should_receive('sell_limit') \
        .with_args('USDT-BTC', 1, 8000) \
        .and_return({'success': True, 'result': {'uuid': 'abcd'}}) \
        .once()
    market = BittrexMarket(client_v1, mock_client_v2())

    order = market.create_sell_order(DUMMY_LIMIT_ORDER)

    assert '16fd2706-8baf-433b-82eb-8c7fada847da' == str(order.order_id)
    assert 'abcd' == order.id_on_market


def test_create_buy_order():
    client_v1 = flexmock()
    client_v1 \
        .should_receive('buy_limit') \
        .with_args('USDT-BTC', 1, 8000) \
        .and_return({'success': True, 'result': {'uuid': 'abcd'}}) \
        .once()
    market = BittrexMarket(client_v1, mock_client_v2())

    order = market.create_buy_order(DUMMY_LIMIT_ORDER)

    assert '16fd2706-8baf-433b-82eb-8c7fada847da' == str(order.order_id)
    assert 'abcd' == order.id_on_market


def test_market_order_not_implemented():
    market = BittrexMarket(flexmock(), mock_client_v2())
    with pytest.raises(NotImplementedError):
        market.create_buy_order(DUMMY_MARKET_ORDER)
    with pytest.raises(NotImplementedError):
        market.create_sell_order(DUMMY_MARKET_ORDER)


def test_invalid_order():
    order = copy.deepcopy(DUMMY_LIMIT_ORDER)
    order._type = 'gandalf'

    market = BittrexMarket(flexmock(), mock_client_v2())
    with pytest.raises(ValueError):
        market.create_buy_order(order)
    with pytest.raises(ValueError):
        market.create_sell_order(order)


def test_not_enough_balance():
    order = copy.deepcopy(DUMMY_LIMIT_ORDER)
    order._quantity = Decimal(0.00001)

    market = BittrexMarket(flexmock(), mock_client_v2())
    with pytest.raises(NotEnoughBalanceToPerformOrderException):
        market.create_buy_order(order)
    with pytest.raises(NotEnoughBalanceToPerformOrderException):
        market.create_sell_order(order)


def test_cancel_order():
    client_v1 = flexmock()
    client_v1.should_receive('cancel').with_args('abcd').and_return({'success': True}).once()

    market = BittrexMarket(client_v1, mock_client_v2())
    market.cancel_order('abcd')


def test_buy_max_available():
    client_v1 = flexmock()
    client_v1 \
        .should_receive('buy_limit') \
        .with_args('USDT-BTC', 9975, 100) \
        .and_return({'success': True, 'result': {'uuid': 'abcd'}}) \
        .once()

    market = BittrexMarket(client_v1, mock_client_v2())
    market.buy_max_available(BTC_USD_PAIR)


def test_sell_max_available():
    client_v1 = flexmock()
    client_v1 \
        .should_receive('sell_limit') \
        .with_args('USDT-BTC', MY_BTC_BALANCE, 100) \
        .and_return({'success': True, 'result': {'uuid': 'abcd'}}) \
        .once()

    market = BittrexMarket(client_v1, mock_client_v2())
    market.sell_max_available(BTC_USD_PAIR)


def test_result_validation():
    BittrexMarket._validate_result({'success': True})

    with pytest.raises(BittrexMarketRequestException):
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
