#!/usr/bin/env bash
set -o errexit

start() { echo travis_fold':'start:$1; echo $1; }
end() { echo travis_fold':'end:$1; }

start test
PYTHONPATH=context python -m unittest discover -s tests --verbose
end test

start format
flake8
end format

start docker
TAG=heatmap-scatter-dash
docker build --tag $TAG context

PORT=8888
docker run --detach --publish $PORT:80 $TAG

until curl --silent --fail http://localhost:$PORT/ > /dev/null; do
    echo 'not up yet'
    sleep 1
done
end docker