Build: [![CircleCI](https://circleci.com/gh/Achse/coinrat.svg?style=svg&circle-token=33676128239f1d0da010339bfbfb34a0d42576b0)](https://circleci.com/gh/Achse/coinrat)

> **Note**: This project was started as Thesis at ČVUT FIT. [Assignment of diploma thesishere](docs/cvut.md) (and semester work for [Python Course](http://naucse.python.cz/2017/mipyt-zima/)).

# CoinRat
Coinrat is modular auto-trading platform focused on crypto-currencies. This is repository is contains platform itself
and also default plugins fot basic usage and inspiration. There is also [UI-App](https://github.com/achse/coinrat_ui)
to help you run simulations and visualize results. 

## Security warning 
> :squirrel: **DISCLAIMER**: The software is provided "as is", without warranty of any kind. For more see: [LICENSE](LICENSE)

* :bangbang: Be very cautious what you run against real Stock Market account. **Test your strategy and configuration well before real trading.**  
* :bangbang: **Protect API KEYS** make sure you **NEVER expose `.env`** file to anyone. If you run this on server, make sure it's well secured.
* :bangbang: **Never expose UI nor port for socket connection on the production server.** 
    * If you need running socket server in production, **ALWAYS** run UI-App locally and use [ssh tunnel](https://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html). 
    * Make sure that socket server is **NEVER** accessible from the internet.

## Installation
* Coinrat core has dependency only on **Python** :snake: and **RabbitMQ** :rabbit:.
    * Following [official instructions](https://www.rabbitmq.com/install-debian.html) to install rabbit.

* If you want to use default storage plugin (recommended), you will need **Influx DB** installed.
    * https://portal.influxdata.com/downloads#influxdb and https://github.com/influxdata/influxdb
    * Start fb: `sudo service influxdb start`
    * `curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE DATABASE coinrat"`
    * For development usage you can use `root` but in production, **always create separate user with limited access**:
        * Create user: `curl -XPOST "http://localhost:8086/query" --data-urlencode "q=CREATE USER coinrat WITH PASSWORD '<password>'"`
        * Grand this user with R+W access to the database: `curl -XPOST "http://localhost:8086/query" --data-urlencode 'q=GRANT ALL ON "coinrat" TO "coinrat"'`

* Create [virtual-env](http://docs.python-guide.org/en/latest/dev/virtualenvs/) and install Python dependencies
    * `python3.6 -m venv __venv__`
    * `. __venv__/bin/activate`
    * `python -m pip install --upgrade git+https://github.com/ericsomdahl/python-bittrex.git` ([Package on Pypi](https://pypi.python.org/pypi/bittrex/0.1.4) is not up to date.) 
    * `python -m pip install -r requirements.txt`
    * `cp .env_example .env`
    * Configure `.env`
    
## Plugins
Platform has five plugin types that are registered in `setup.py`: 
* **`coinrat_market_plugins`** - This plugin provides one or more **stock-market connections** (Bitfinex, Bittrex, ...) and platform uses those plugin create order, check balances, ...
    * You can check available markets by: `python -m coinrat markets`
* **`coinrat_candle_storage_plugins`** - This plugin provides **storage for candles** (stock-market price data).
    * You can check available candle storages by: `python -m coinrat candle_storages`
* **`coinrat_order_storage_plugins`** - This plugin provides **storage for orders** that are created by strategies in platform.
    * You can check available order storages by: `python -m coinrat order_storages`
* **`coinrat_synchronizer_plugins`** - This plugin is responsible for **pumping stock-market data (candles) into platform**. Usually one module contains both market and synchronizer plugin (for stock-market modules). But for read only sources (eg. cryptocompare.com) can be provided solely in the module.
    * You can check available synchronizers by: `python -m coinrat synchronizers`
* **`coinrat_strategy_plugins`** - Most interesting plugins. Represents one **trading strategy**. Strategy runs with one instance of candle and order storage, but in theory can use multiple markets (for example for [Market Arbitrage](https://www.investopedia.com/terms/m/marketarbitrage.asp))
    * You can check available strategies by: `python -m coinrat strategies`

## Feed data from stock markets
Fist, we need stock-market data. There are two synchonizers in default plugins
* `python -m coinrat synchronize bittrex USD BTC`
* `python -m coinrat synchronize cryptocompare USD BTC`

This process must always be running to keep you with current stock-market data.

## Usage for simulations and visualisation in UI-App
Once we have data we can see them in the UI-App.

* We need to start socket server: `python -m coinrat start_server`, keep it running
* You can configure the port of the socket server in `.env`  
* For strategy simulation started from UI-App we need to have process that will handle them. Start one by: `python -m coinrat start_task_consumer`
* Follow [instructions here](https://github.com/achse/coinrat_ui) to install and run the UI-App.

## Basic usage against real market
> :bangbang: **This will execute strategy against real market!** One good option for testing is to create separate account on the stockmarket wtih **very** limited resources on it.

Run one of default strategies with this command: `python -m coinrat run_strategy double_crossover USD BTC bittrex` 

## Additional tips & tricks
* There is visualization tool for Influx DB called [Chronograf](https://github.com/influxdata/chronograf), it can be usefull for visualizing data too.
