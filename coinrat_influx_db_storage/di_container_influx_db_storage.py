import os
from typing import Dict

from influxdb import InfluxDBClient

from coinrat.di_container import DiContainer
from coinrat.domain.order import OrderStorage
from .portfolio_snapshot_storage import PortfolioSnapshotInnoDbStorage, PORTFOLIO_SNAPSHOT_STORAGE_NAME
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
            'portfolio_snapshot_storage': {
                'instance': None,
                'factory': lambda: PortfolioSnapshotInnoDbStorage(self.influxdb_client)
            },
        }

        self._order_storages: Dict[str, OrderStorage] = {}

    def get_order_storage(self, name: str) -> OrderStorage:
        if name.startswith(ORDER_STORAGE_NAME):
            measurement_name = name.split('_')[-1]
            if measurement_name not in self._order_storages:
                self._order_storages[measurement_name] = OrderInnoDbStorage(self.influxdb_client, measurement_name)
            return self._order_storages[measurement_name]

        raise ValueError('Order storage "{}" not supported by this plugin.'.format(name))

    def get_candle_storage(self, name: str) -> CandleInnoDbStorage:
        if name == CANDLE_STORAGE_NAME:
            return self._get('candle_storage')

        raise ValueError('Candle storage "{}" not supported by this plugin.'.format(name))

    def get_portfolio_snapshot_storage(self, name) -> PortfolioSnapshotInnoDbStorage:
        if name == PORTFOLIO_SNAPSHOT_STORAGE_NAME:
            return self._get('portfolio_snapshot_storage')

        raise ValueError('Candle storage "{}" not supported by this plugin.'.format(name))

    @property
    def influxdb_client(self):
        return self._get('influxdb_client')
