DUMMY_ORDER_ID_ON_MARKET = '42ac7063-928f-41e2-b7d3-c06d5fa69203'

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

OPEN_ORDER = {
    'success': True,
    'message': '',
    'result': {
        'AccountId': None,
        'OrderUuid': DUMMY_ORDER_ID_ON_MARKET,
        'Exchange': 'USDT-BTC',
        'Type': 'LIMIT_SELL',
        'Quantity': 0.00310976,
        'QuantityRemaining': 0.00310976,
        'Limit': 8946.999975,
        'Reserved': 0.00310976,
        'ReserveRemaining': 0.00310976,
        'CommissionReserved': 0.0,
        'CommissionReserveRemaining': 0.0,
        'CommissionPaid': 0.0,
        'Price': 0.0,
        'PricePerUnit': None,
        'Opened': '2017-11-26T13:08:10.763',
        'Closed': None,
        'IsOpen': True,
        'Sentinel': '7823f66f-15e8-4d23-a43a-b025c48f6f6f',
        'CancelInitiated': False,
        'ImmediateOrCancel': False,
        'IsConditional': False,
        'Condition': 'NONE',
        'ConditionTarget': None
    }
}
CLOSED_ORDER = {
    'success': True,
    'message': '',
    'result': {
        'AccountId': None,
        'OrderUuid': DUMMY_ORDER_ID_ON_MARKET,
        'Exchange': 'USDT-BTC',
        'Type': 'LIMIT_SELL',
        'Quantity': 0.00310976,
        'QuantityRemaining': 0.0,
        'Limit': 8946.999975,
        'Reserved': 0.00310976,
        'ReserveRemaining': 0.00310976,
        'CommissionReserved': 0.0,
        'CommissionReserveRemaining': 0.0,
        'CommissionPaid': 0.06955755,
        'Price': 27.82302263,
        'PricePerUnit': 8946.99997105,
        'Opened': '2017-11-26T13:08:10.763',
        'Closed': '2017-11-26T13:08:14.497',
        'IsOpen': False,
        'Sentinel': '9cb4113d-c780-40a2-bf5e-86864d9b292b',
        'CancelInitiated': False,
        'ImmediateOrCancel': False,
        'IsConditional': False,
        'Condition': 'NONE',
        'ConditionTarget': None
    }
}
