.. image:: https://circleci.com/gh/Achse/coinrat.svg?style=svg&circle-token=d0173e6f1bf5c0ea2c28c6219ee841c4be74eef0
:target: https://circleci.com/gh/Achse//coinrat

Coinrat
=======

Modular auto-trading crypto-currency platform.

Installation
============

InfluxDb
* https://portal.influxdata.com/downloads#influxdb and https://github.com/influxdata/influxdb
* Start fb: ``sudo service influxdb start``
* ``curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE DATABASE coinrat"``

Chronograph (Influx UI tool)
* https://portal.influxdata.com/downloads and https://github.com/influxdata/chronograf
* ``service chronograf start``

Development (Python & Requirements)
* ``python3.6 -m venv __venv__``
* ``. __venv__/bin/activate``
* ``python3 -m pip install --upgrade git+https://github.com/ericsomdahl/python-bittrex.git``
* ``python -m pip install -r requirements.txt``
