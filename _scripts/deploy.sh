#!/usr/bin/env bash

echo 'Killing all coinrat...'
ps aux | grep 'python -m coinrat' | tr -s ' ' | cut -d' ' -f2 | xargs kill -15

echo 'Clearing logs...'
rm -fr logs/*
rm -fr nohup.out

echo 'Fetching code...'
git fetch origin
git reset origin/master --hard
