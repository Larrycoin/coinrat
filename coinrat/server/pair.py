from coinrat.domain import Pair


def parse_pair(raw_pair: str) -> Pair:
    pair_data = raw_pair.split('_')
    return Pair(pair_data[0], pair_data[1])
