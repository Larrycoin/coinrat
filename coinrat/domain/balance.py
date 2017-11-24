from decimal import Decimal


class Balance:
    """
    Amount of given Currency available on the given Market.
    """

    def __init__(self, market_name: str, currency: str, available_amount: Decimal) -> None:
        assert isinstance(available_amount, Decimal)

        self._market_name = market_name
        self._currency = currency
        self._available_amount = available_amount

    @property
    def market_name(self):
        return self._market_name

    @property
    def currency(self):
        return self._currency

    @property
    def available_amount(self) -> Decimal:
        return self._available_amount

    def __repr__(self):
        return '{0:.8f} {1}'.format(self._available_amount, self._currency)
