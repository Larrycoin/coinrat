#!/usr/bin/env bash

cd /home/coinrat/coinrat

export LC_ALL=en_US.utf-8
export LANG=en_US.utf-8;

pipenv run coinrat synchronize cryptocompare USD BTC --candle_storage influx_db
