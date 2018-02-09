#!/usr/bin/env bash
set -o errexit

# xtrace turned on only within the travis folds
start() { echo travis_fold':'start:$1; echo $1; set -v; }
end() { set +v; echo travis_fold':'end:$1; }
die() { set +v; echo "$*" 1>&2 ; exit 1; }

start test
PYTHONPATH=context python -m unittest discover -s tests --verbose
end test


start format
flake8 context || die "Run 'autopep8 --in-place -r context'"
end format


start isort
isort --recursive context --check-only || die "Run 'isort --recursive context'"
end isort


start pip
# TODO: Uncomment this once requirements-freeze.txt is in master
#URL_BASE=https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/master
# ! ( diff <(cat context/requirements.txt; cat requirements-dev.txt) \
#         <(curl --silent $URL_BASE/context/requirements.txt; curl --silent $URL_BASE/requirements-dev.txt) \
#    || diff requirements-freeze.txt <(curl --silent $URL_BASE/requirements-freeze.txt) ) ||
#die 'If non-frozen requirements files change, so should the frozen one, and vice versa.'
end pip


start usage
diff <(perl -ne 'print if /^usage:/../^  --api_prefix/' README.md) <(cd context; ./app_runner.py -h) || \
die '
Update README.md:
  perl -ne '"'"'print unless /^usage:/../^  --api_prefix/; print `cd context; ./app_runner.py -h` if /^usage:/'"'"' -i README.md'
end usage


start cypress
python context/app_runner.py --files fixtures/good/data/counts.csv --diffs fixtures/good/data/stats-* --port 8888 &
node_modules/.bin/cypress run
kill `jobs -p`
end cypress


start docker
source define_repo.sh

# We don't want to run the whole script under sudo on Travis,
# because then it gets the system python instead of the version
# we've specified.
OPT_SUDO=''
if [ ! -z "$TRAVIS" ]; then
  OPT_SUDO='sudo'
fi

echo "REPO: $REPO"
echo "IMAGE: $IMAGE"

$OPT_SUDO docker pull $REPO
$OPT_SUDO docker build --cache-from $REPO --tag ${IMAGE}_base context
$OPT_SUDO docker build --cache-from ${IMAGE}_base --tag ${IMAGE}_refinery --file context/Dockerfile.refinery context

PORT=8888
CONTAINER_NAME=$IMAGE-container
# Preferred syntax, Docker version >= 17.06
#    --mount type=bind,src=$(pwd)/fixtures/good/input.json,dst=/data/input.json \
#    --mount type=volume,target=/refinery-data/ \
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    --volume $(pwd)/fixtures/good/input.json:/data/input.json \
    --volume /refinery-data/ \
    ${IMAGE}_refinery
    # TODO : volume mounting

TRIES=1
until curl --silent --fail http://localhost:$PORT/ > /dev/null; do
    echo "$TRIES: not up yet"
    if (( $TRIES > 5 )); then
        $OPT_SUDO docker logs $CONTAINER_NAME
        die "HTTP requests to app in Docker container never succeeded"
    fi
    (( TRIES++ ))
    sleep 1
done
echo "docker is responsive"

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
echo "container cleaned up"
end docker
