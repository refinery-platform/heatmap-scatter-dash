#!/usr/bin/env bash
set -o errexit

# xtrace turned on only within the travis folds
start() { echo travis_fold':'start:$1; echo $1; set -v; }
end() { set +v; echo travis_fold':'end:$1; echo; echo; }
die() { set +v; echo "$*" 1>&2 ; exit 1; }
retry() {
    TRIES=1
    until curl --silent --fail http://localhost:$PORT/ > /dev/null; do
        echo "$TRIES: not up yet"
        if (( $TRIES > 10 )); then
            $OPT_SUDO docker logs $CONTAINER_NAME
            die "HTTP requests to app never succeeded"
        fi
        (( TRIES++ ))
        sleep 1
    done
}
PORT=8888


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
# Request from githubusercontent.com was failing...
#URL_BASE=https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/master
#DIFF_RAW=$(diff <(cat context/requirements.txt; \
#                      cat requirements-dev.txt) \
#                <(curl --silent $URL_BASE/context/requirements.txt; \
#                  curl --silent $URL_BASE/requirements-dev.txt))
#DIFF_FREEZE=$(diff requirements-freeze.txt <(curl --silent $URL_BASE/requirements-freeze.txt))
#[ "$DIFF_RAW" ] && [ -z "$DIFF_FREEZE" ] && \
#  die "If raw changes, freeze should change: '$DIFF_RAW'"
#[ -z "$DIFF_RAW" ] && [ "$DIFF_FREEZE" ] && \
#  die "If freeze changes, raw should change: '$DIFF_FREEZE'"
end pip


start usage
diff <(perl -ne 'print if /^usage:/../^  --api_prefix/' README.md) \
     <(cd context; ./app_runner.py -h) || \
die '
Update README.md:
  perl -ne '"'"'print unless /^usage:/../^  --api_prefix/; print `cd context; ./app_runner.py -h` if /^usage:/'"'"' -i README.md'
end usage


start refinery_data_envvar
# Since the input.json specifies a data directory which might not exist,
# and we want to minimize changes to the host running the test,
# we will check the other modes with the docker tests.
FIXTURES_URL_BASE='https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/v0.1.3/fixtures'
FILE_URLS="$FIXTURES_URL_BASE/good/data/counts-copy.csv.gz" \
DATA_DIR='/tmp' \
python context/app_runner_refinery.py --input /no/such/file --port $PORT &
retry
kill `jobs -p`
end refinery_data_envvar


start cypress
diff fixtures/good/data/counts.csv \
     <(gunzip --to-stdout fixtures/good/data/counts-copy.csv.gz) || \
die 'Zip file should match raw file'
python context/app_runner.py \
  --files fixtures/good/data/counts* \
  --diffs fixtures/good/data/stats-* \
  --metas fixtures/good/data/metadata.* \
  --port $PORT &
node_modules/.bin/cypress run
kill `jobs -p`
end cypress


start docker_build
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
$OPT_SUDO docker build --cache-from $REPO --tag $IMAGE context
end docker_build


start docker_json_file
CONTAINER_NAME=$IMAGE-container
# Preferred syntax, Docker version >= 17.06
#    --mount type=bind,src=$(pwd)/fixtures/good/input.json,dst=/data/input.json \
#    --mount type=volume,target=/refinery-data/ \
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    --volume $(pwd)/fixtures/good/input.json:/data/input.json \
    --volume /refinery-data/ \
    $IMAGE
retry
docker stop $CONTAINER_NAME | xargs docker rm
end docker_json


start docker_json_envvar
INPUT_JSON=`cat $(pwd)/fixtures/good/input.json`
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    --volume /refinery-data/ \
    -e "INPUT_JSON=$INPUT_JSON" \
    $IMAGE
retry
docker stop $CONTAINER_NAME | xargs docker rm
end docker_json_envvar


start docker_json_url_envvar
INPUT_JSON_URL="$FIXTURES_URL_BASE/good/input.json"
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    --volume /refinery-data/ \
    -e "INPUT_JSON_URL=$INPUT_JSON_URL" \
    $IMAGE
retry
docker stop $CONTAINER_NAME | xargs docker rm
end docker_json_url_envvar


start docker_envvars
FILE_URLS="$FIXTURES_URL_BASE/good/data/counts.csv"
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    -e "FILE_URLS=$FILE_URLS" \
    $IMAGE
retry
docker stop $CONTAINER_NAME | xargs docker rm
end docker_envvars