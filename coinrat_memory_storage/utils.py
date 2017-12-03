from coinrat.domain import Pair


def create_pair_identifier(pair: Pair) -> str:
    return '{}_{}'.format(pair.base_currency, pair.market_currency)
