#!/usr/bin/env bash
python -m pip freeze | grep -v -e "pkg-resources" -e "python-bittrex" -e "coinrat=="> requirements.txt
