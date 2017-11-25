#!/usr/bin/env bash

python -m pytest tests --pyargs . --cov=. --cov-config .coveragerc --cov-report html
