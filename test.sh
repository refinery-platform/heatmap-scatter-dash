#!/usr/bin/env bash
set -o errexit

# xtrace turned on only within the travis folds
start() { echo travis_fold':'start:$1; echo $1; set -v; }
end() { set +v; echo travis_fold':'end:$1; }
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


start cli
FIXTURES='https://raw.githubusercontent.com/refinery-platform/heatmap-scatter-dash/v0.1.3/fixtures/good/data'
FILE_URLS="$FIXTURES/counts.csv" \
DATA_DIR='/tmp/heatmap-data' \
python context/app_runner_refinery.py --input /no/such/file --port $PORT &
retry
kill `jobs -p`
end cli


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


start docker_json
CONTAINER_NAME=$IMAGE-container
# Preferred syntax, Docker version >= 17.06
#    --mount type=bind,src=$(pwd)/fixtures/good/input.json,dst=/data/input.json \
#    --mount type=volume,target=/refinery-data/ \
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    --volume $(pwd)/fixtures/good/input.json:/data/input.json \
    --volume /refinery-data/ \
    $IMAGE

retry
echo "docker is responsive with input.json"

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
echo "container cleaned up"
end docker_json


start docker_envvars
$OPT_SUDO docker run --name $CONTAINER_NAME --detach --publish $PORT:80 \
    -e "FILE_URLS=$FIXTURES/counts.csv" \
    $IMAGE
retry
echo "docker is responsive with envvars"

docker stop $CONTAINER_NAME
docker rm $CONTAINER_NAME
echo "container cleaned up"
end docker_envvars