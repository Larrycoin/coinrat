from typing import Dict, List

from coinrat.domain.order import Order, OrderExporter


def serialize_order(order: Order) -> Dict:
    return OrderExporter.serialize_order_to_json_serializable(order)


def serialize_orders(orders: List[Order]) -> List[Dict]:
    return list(map(serialize_order, orders))


def parse_order(data: Dict) -> Order:
    return OrderExporter.create_order_from_data(data)
