.. image:: https://circleci.com/gh/Achse/coinrat.svg?style=svg&circle-token=d0173e6f1bf5c0ea2c28c6219ee841c4be74eef0
:target: https://circleci.com/gh/Achse//coinrat

Coinrat
=======

Modular auto-trading crypto-currency platform.

Installation
============

InfluxDb (Ubuntu/Debian):
* https://portal.influxdata.com/downloads#influxdb and https://github.com/influxdata/influxdb
* Start fb: ``sudo service influxdb start``
* ``curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE DATABASE coinrat"``

