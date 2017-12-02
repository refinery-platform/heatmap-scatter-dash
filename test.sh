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


start isort
echo "Run 'isort -rc .' locally to fix any problems."
isort -r . --check-only
end isort


start docker
source define_repo.sh

# We don't want to run the whole script under sudo on Travis,
# because then it gets the system python instead of the version
# we've specified.
OPT_SUDO=''
if [ ! -z "$TRAVIS" ]; then
  OPT_SUDO='sudo'
fi

$OPT_SUDO docker pull $REPO
$OPT_SUDO docker build  --cache-from $REPO --tag $IMAGE context

PORT=8888
$OPT_SUDO docker run --name $IMAGE-container --detach --publish $PORT:80 $IMAGE

TRIES=1
until curl --silent --fail http://localhost:$PORT/ > /dev/null; do
    echo "$TRIES: not up yet"
    if (( $TRIES > 3 )); then
        echo "HTTP requests to app in Docker container never succeeded"
        $OPT_SUDO docker logs $IMAGE-container
        exit 1
    fi
    (( TRIES++ ))
    sleep 1
done
echo "docker is responsive"

docker stop $IMAGE-container
docker rm $IMAGE-container
echo "container cleaned up"
end docker
