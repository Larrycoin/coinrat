from decimal import Decimal


def to_decimal(value) -> Decimal:
    if type(value) in [str, int]:
        return Decimal(str(value))

    if type(value) is float:
        return Decimal(value).quantize(Decimal('0.000000001'))

    raise ValueError('Provided value (of type: {}) is not valid for decimal conversion'.format(str(type(value))))
