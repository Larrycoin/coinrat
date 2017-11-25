#!/usr/bin/env bash
# Script for developer to run easily tests locally during development
python -m pytest tests --maxfail=1 --pyargs . --cov=. --cov-config .coveragerc --cov-report html $1 $2 $3 $4 $5
