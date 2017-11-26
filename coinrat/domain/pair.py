from .coinrat import ForEndUserException


class MarketPairDoesNotExistsException(ForEndUserException):
    pass


class Pair:
    def __init__(self, base_currency: str, market_currency: str) -> None:
        assert base_currency != 'USDT', \
            'Some markets use USDT instead of USD, this is impl. detail of that market, use USD otherwise'
        assert market_currency not in ['USDT', 'USD'], \
            'This is probably error. Pairs are not usually represented in USD as market_currency'

        self._base_currency = base_currency
        self._market_currency = market_currency

    @property
    def base_currency(self) -> str:
        return self._base_currency

    @property
    def market_currency(self) -> str:
        return self._market_currency

    def __repr__(self):
        return '{}-{}'.format(self._base_currency, self._market_currency)
