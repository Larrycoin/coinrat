#!/usr/bin/env bash

echo 'Fetching code...'
git fetch origin
git reset origin/master --hard

echo 'Killing all coinrat...'
ps aux | grep 'python -m coinrat' | tr -s ' ' | cut -d' ' -f2 | xargs kill -15

echo 'Clearing logs...'
rm -fr logs/*
rm -fr nohup.out

echo 'Starting new coinrat processes...'
nohup python -m coinrat synchronize cryptocompare USD BTC &
nohup python -m coinrat run_strategy double_crossover USD BTC bittrex &
