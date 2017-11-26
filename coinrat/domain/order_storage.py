from .order import Order


class OrderStorage:
    def save_order(self, order: Order) -> None:
        raise NotImplementedError()
