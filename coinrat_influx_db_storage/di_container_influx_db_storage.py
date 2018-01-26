import os

from influxdb import InfluxDBClient

from coinrat.di_container import DiContainer
from coinrat.domain.order import OrderStorage
from .candle_storage import CandleInnoDbStorage, CANDLE_STORAGE_NAME
from .order_storage import OrderInnoDbStorage, ORDER_STORAGE_NAME


class DiContainerInfluxDbStorage(DiContainer):

    def __init__(self) -> None:
        super().__init__()

        self._storage = {
            'influxdb_client': {
                'instance': None,
                'factory': lambda: InfluxDBClient(
                    os.environ.get('STORAGE_INFLUX_DB_HOST'),
                    os.environ.get('STORAGE_INFLUX_DB_PORT'),
                    os.environ.get('STORAGE_INFLUX_DB_USER'),
                    os.environ.get('STORAGE_INFLUX_DB_PASSWORD'),
                    os.environ.get('STORAGE_INFLUX_DB_DATABASE'),
                ),
            },
            'candle_storage': {
                'instance': None,
                'factory': lambda: CandleInnoDbStorage(self.influxdb_client)
            },
        }

        self._order_storages = {}

    def get_order_storage(self, name: str) -> OrderStorage:
        if name.startswith(ORDER_STORAGE_NAME):
            measurement_name = name.split('_')[-1]
            if measurement_name not in self._order_storages:
                self._order_storages[measurement_name] = OrderInnoDbStorage(self.influxdb_client, measurement_name)
            return self._order_storages[measurement_name]

        raise ValueError('Order storage "{}" not supported by this plugin.'.format(name))

    def get_candle_storage(self, name):
        if name == CANDLE_STORAGE_NAME:
            return self._get('candle_storage')

        raise ValueError('Candle storage "{}" not supported by this plugin.'.format(name))

    @property
    def influxdb_client(self):
        return self._get('influxdb_client')
