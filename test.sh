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
source define_repo.sh
# TODO: docker pull $REPO

docker build --tag $IMAGE context
# TODO: --cache-from $REPO

PORT=8888
docker run --detach --publish $PORT:80 $IMAGE

until curl --silent --fail http://localhost:$PORT/ > /dev/null; do
    echo "not up yet"
    sleep 1
done
echo "docker is responsive"
end docker