from influxdb import InfluxDBClient

from coinrat.domain import OrderStorage, Order

ORDER_STORAGE_NAME = 'influx_db'


class OrderInnoDbStorage(OrderStorage):
    def __init__(self, influx_db_client: InfluxDBClient):
        self._client = influx_db_client

    def save_order(self, order: Order) -> None:
        raise NotImplementedError('Todo: implement')  # Todo: implement
