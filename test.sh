#!/usr/bin/env bash
set -o errexit

# xtrace turned on only within the travis folds
start() { echo travis_fold':'start:$1; echo $1; set -x; }
end() { set +x; echo travis_fold':'end:$1; }
die() { echo "$*" 1>&2 ; exit 1; }

start test
PYTHONPATH=context python -m unittest discover -s tests --verbose
end test


start format
flake8 || die "Run 'autopep8 --in-place -r .'"
end format


start isort
isort -r . --check-only || die "Run 'isort -rc .'"
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
    if (( $TRIES > 5 )); then
        $OPT_SUDO docker logs $IMAGE-container
        die "HTTP requests to app in Docker container never succeeded"
    fi
    (( TRIES++ ))
    sleep 1
done
echo "docker is responsive"

docker stop $IMAGE-container
docker rm $IMAGE-container
echo "container cleaned up"
end docker
