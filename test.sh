#!/usr/bin/env bash
set -o errexit

start() { echo travis_fold':'start:$1; echo $1; }
end() { echo travis_fold':'end:$1; }

start test
python -m unittest discover -s tests --verbose
end test

start format
flake8
end format