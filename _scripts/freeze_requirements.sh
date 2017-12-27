#!/usr/bin/env bash
# Script for developer
python -m pip freeze | grep -v -e "pkg-resources" -e "python-bittrex" -e "coinrat==" -e "git+git@github.com:Achse" > requirements.txt
