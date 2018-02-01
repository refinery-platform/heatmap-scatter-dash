#!/usr/bin/env bash
set -o errexit

eb init
echo '# Do not edit by hand. / Do not check in.' > requirements.txt
pipenv lock --requirements >> requirements.txt  # gitignored
eb create heatmap-scatterplot
eb status | grep CNAME | sed 's/CNAME: /http:\/\//'