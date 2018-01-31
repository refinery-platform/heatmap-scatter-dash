#!/usr/bin/env bash
set -o errexit

eb init
pipenv lock --requirements > requirements.txt  # gitignored
eb create heatmap-scatterplot
eb status | grep CNAME | sed 's/CNAME: /http:\/\//'