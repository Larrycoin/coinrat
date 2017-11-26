from influxdb import InfluxDBClient


def get_all_from_influx_db(influx_database: InfluxDBClient, measurement: str):
    return list(influx_database.query('SELECT * FROM "{}"'.format(measurement)).get_points())
