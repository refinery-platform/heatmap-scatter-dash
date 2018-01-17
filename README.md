# heatmap-scatter-dash

A heatmap-scatterplot using [Dash by plotly](https://plot.ly/products/dash/).
Can be run as a Flask app from the commandline,
or as Docker container for [Refinery](https://github.com/refinery-platform/refinery-platform) visualizations.

<img width="645" alt="screen shot" src="https://user-images.githubusercontent.com/730388/34791348-b263ab92-f612-11e7-8330-31a2d4804ada.png">

```
$ python app_runner.py -h
usage: app_runner.py [-h] (--demo ROWS COLS | --files CSV [CSV ...])
                     [--diffs CSV [CSV ...]] [--most_variable_rows ROWS]
                     [--cluster_rows] [--cluster_cols]
                     [--colors {Greys,YlGnBu,Greens,YlOrRd,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,Hot,Blackbody,Earth,Electric,Viridis}]
                     [--reverse_colors] [--html_error] [--api_prefix PREFIX]
                     [--debug] [--port PORT]

Light-weight visualization for differential expression

optional arguments:
  -h, --help            show this help message and exit
  --demo ROWS COLS      Generates a random matrix with the rows and columns
                        specified.
  --files CSV [CSV ...]
                        Read CSV or TSV files. Identifiers should be in the
                        first column and multiple files will be joined on
                        identifier. Compressed files are also handled, if
                        correct extension is given. (ie ".csv.gz")
  --diffs CSV [CSV ...]
                        Read CSV or TSV files containing differential
                        expression data.
  --most_variable_rows ROWS
                        For the heatmap, we first sort by row variance, and
                        then take the number of rows specified here. Defaults
                        to 500.
  --cluster_rows        For the heatmap, hierarchically cluster rows.
  --cluster_cols        For the heatmap, hierarchically cluster columns.
  --colors {Greys,YlGnBu,Greens,YlOrRd,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,Hot,Blackbody,Earth,Electric,Viridis}
                        Color scale for the heatmap. Defaults to grey scale.
  --reverse_colors      Reverse the color scale of the heatmap.
  --html_error          If there is a configuration error, instead of exiting,
                        start the server and display an error page. (This is
                        used by Refinery.)
  --api_prefix PREFIX   Prefix for API URLs. (This is used by Refinery.)
  --debug               Run the server in debug mode: The server will restart
                        in response to any code changes, and some hidden
                        fields will be shown.
  --port PORT           Specify a port to run the server on. Defaults to 8050.
```

## Getting Started

Check out the project and install dependencies:
```bash
  # Requires Python3:
$ python --version
$ git clone https://github.com/mccalluc/heatmap-scatter-dash.git
$ cd heatmap-scatter-dash
$ pip install -r context/requirements.txt
```

Then try one of these:

```bash
$ cd context

  # Generate a random matrix:
$ python app_runner.py --demo 100 10

  # Load data from disk:
$ python app_runner.py --files ../fixtures/good/data/counts.csv --diffs ../fixtures/good/data/stats-*

  # Read an input.json like that created by Refinery:
$ python app_runner_refinery.py --input ../fixtures/good/input.json
```

and visit `http://localhost:8050/`.

## Testing

One bash script, `test.sh`, handles all our tests:
- Python unit tests
- Python style tests (`flake8` and `isort`)
- Cypress.io interaction tests
- Docker container build and launch

A few more dependencies are required for this to work locally:
```bash
  # Install Docker: https://www.docker.com/community-edition
$ pip install -r requirements-dev.txt
$ npm install cypress --save-dev
```

## Release

Successful Github tags and PRs will prompt Travis to push the built image to Dockerhub. For a new version number:

```bash
$ git tag v0.0.x && git push origin --tags
```

## For More Information...

There are a few [notes](docs) on implementation decisions and lessons learned.

The [online help](context/app/static/help.md) can be previewed to get a better sense of the operational details.
