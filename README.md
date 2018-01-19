Build: [![CircleCI](https://circleci.com/gh/Achse/coinrat.svg?style=svg&circle-token=33676128239f1d0da010339bfbfb34a0d42576b0)](https://circleci.com/gh/Achse/coinrat)

> **Note**: This project was started as Thesis at ČVUT FIT. [Assignment of diploma thesishere](docs/cvut.md) (and semester work for [Python Course](http://naucse.python.cz/2017/mipyt-zima/)).

# CoinRat
Coinrat is modular auto-trading platform focused on crypto-currencies. This is repository is contains platform itself
and also default plugins fot basic usage and inspiration. There is also [UI-App](https://github.com/achse/coinrat_ui)
to help you run simulations and visualize results. 

# Security warning 
> :squirrel: **DISCLAIMER**: The software is provided "as is", without warranty of any kind. For more see: [LICENSE](LICENSE)

* :bangbang: Be very cautious what you run against real Stock Market account. **Test your strategy and configuration well before real trading.**  
* :bangbang: **Protect API KEYS** make sure you **NEVER expose `.env`** file to anyone. If you run this on server, make sure it's well secured.
* :bangbang: **Never expose UI nor port for socket connection on the production server.** 
    * If you need running socket server in production to be able to connect to it with UI-App, **ALWAYS** run UI-App locally and use [ssh tunnel](https://blog.trackets.com/2014/05/17/ssh-tunnel-local-and-remote-port-forwarding-explained-with-examples.html) and make sure it's not accessible from the internet.

# Installation
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

# Additional tips & tricks
* There is visualization tool for Influx DB called [Chronograf](https://github.com/influxdata/chronograf), it can be usefull for visualizing data too.
