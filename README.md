Build: [![CircleCI](https://circleci.com/gh/Achse/coinrat.svg?style=svg&circle-token=33676128239f1d0da010339bfbfb34a0d42576b0)](https://circleci.com/gh/Achse/coinrat)

> **Note**: This project started as a Thesis project at ČVUT FIT. [Assignment of diploma thesis here](docs/cvut.md) (early stage was developed during [CVUT Python Course](http://naucse.python.cz/2017/mipyt-zima/)).

# CoinRat
Coinrat is modular auto-trading platform focused on crypto-currencies. This repository is contains platform itself
and also default plugins for basic usage and inspiration. There is also [UI-App](https://github.com/achse/coinrat_ui)
to help with running simulations and to visualize results. 

## Security warning 
> :squirrel: **DISCLAIMER**: The software is provided "as is", without warranty of any kind. For more see: [LICENSE](LICENSE)

* :bangbang: Be very cautious what you run against real Stock Market account. **Test your strategy and configuration well before real trading.**  
* :bangbang: **Protect API KEYS** make sure you **NEVER expose `.env`** file to anyone. If you run this on server, make sure it's well secured.
* :bangbang: **Never expose UI nor port for socket connection on the production server.** 
    * If you need running socket server in production, **ALWAYS** run UI-App locally and use [ssh tunnel](https://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html). 
    * Make sure that socket server is **NEVER** accessible from the internet.

## Installation
* Install InfluxDB: [here](https://portal.influxdata.com/downloads#influxdb)
    * Start: `sudo service influxdb start`
    * `curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE DATABASE coinrat"`
    * For development usage you can use `root`, but **always create separate user with limited access per database** in PRODUCTION:
        * Create user: `curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE USER coinrat WITH PASSWORD '<password>'"`
        * Grand this user with R+W access to the database: `curl -XPOST "http://localhost:8086/query" --data-urlencode 'q=GRANT ALL ON "coinrat" TO "coinrat"'`
* Install RabbitMQ :rabbit: [official instructions](https://www.rabbitmq.com/install-debian.html).
* Install MySQL database (MySQL, MariaDB, Percona, ...) and create `coinrat` database and user with write access for it. Add configuration into `.env`
* Install dependencies: `pipenv install`
* Provide configuration `cp .env_example .env`
* Start virtual environment: `pipenv shell`
* Run MySQL database migrations: `pipenv run coinrat database_migrate`.
    
## Plugins
Platform has five plugin types that are registered in `setup.py`: 
* **`coinrat_market_plugins`** - This plugin provides one or more **stock-market connections** (Bitfinex, Bittrex, ...) and platform uses those plugin to create order, check balances, ...
    * You can check available markets by: `pipenv run coinrat markets`
* **`coinrat_candle_storage_plugins`** - This plugin provides **storage for candles** (stock-market price data).
    * You can check available candle storages by: `pipenv run coinrat candle_storages`
* **`coinrat_order_storage_plugins`** - This plugin provides **storage for orders** that are created by strategies in platform.
    * You can check available order storages by: `pipenv run coinrat order_storages`
* **`coinrat_synchronizer_plugins`** - This plugin is responsible for **pumping stock-market data (candles) into platform**. Usually one module contains both market and synchronizer plugin (for stock-market modules). But for read only sources (eg. cryptocompare.com) can be provided solely in the module.
    * You can check available synchronizers by: `pipenv run coinrat synchronizers`
* **`coinrat_strategy_plugins`** - Most interesting plugins. Contains **trading strategies**. Strategy runs with one instance of candle and order storage, but can use multiple markets (for [Market Arbitrage](https://www.investopedia.com/terms/m/marketarbitrage.asp), etc...)
    * You can check available strategies by: `pipenv run coinrat strategies`

## Configuration for markets and strategies
Each strategy (or market) can have special configuration. You can see it by running 
`pipenv run coinrat market <market_name>` / `pipenv run coinrat strategy <strategy_name>`.

You can create JSON file with specific properties and provide it via `-c` option to `run_strategy` command.

> (Markets have configuration, but providing it into `run_strategy` command is not implemented yet. See [#18](https://github.com/Achse/coinrat/issues/18) for more info and workaround.)

## Feed data from stock markets
Fist, we need stock-market data. There are two synchronizers in default plugins:
* `pipenv run coinrat synchronize bittrex USD BTC`
* `pipenv run coinrat synchronize cryptocompare USD BTC`

This process must always be running to keep you with current stock-market data.

## Usage for simulations and visualisation in UI-App
Once we have data you can see them in the UI-App.

* Start socket server: `pipenv run coinrat start_server` and keep it running (You can configure the port of the socket server in `.env`)  .
* For strategy simulation started from UI-App, we need to have process that will handle them. Start one by: `pipenv run coinrat start_task_consumer`.
* Follow [instructions here](https://github.com/achse/coinrat_ui) to install and run the UI-App.

## Basic usage against real market
> :bangbang: **This will execute strategy against real market!** One good option for testing (if market does not provide test account) is to create separate account on the stock-market with **very** limited resources on it.

Run one of default strategies with this command: `pipenv run coinrat run_strategy double_crossover USD BTC bittrex --candle_storage influx_db --order_storage influx_db_orders-A` 

## Troubleshooting
1. **OSError: mysql_config not found** → Install: `sudo apt-get install libmysqlclient-dev`
2. **ERROR: For market "bittrex" no candles in storage "influx_db".** → No data for given **market**, **storage** and selected **time period** / your time interval is too small.
3. **Every second candle is missing.** → See [#29](https://github.com/Achse/coinrat/issues/29).

## Additional tips & tricks
* There is visualization tool for Influx DB called [Chronograf](https://github.com/influxdata/chronograf), it can be useful for visualizing data too.
