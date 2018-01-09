# heatmap-scatter-dash

A heatmap-scatterplot using [Dash by plotly](https://plot.ly/products/dash/).
Can be run as a Flask app from the commandline,
or as Docker container for [Refinery](https://github.com/refinery-platform/refinery-platform) visualizations.

<img width="657" alt="heatmap-scatterplot" src="https://user-images.githubusercontent.com/730388/34022648-6bd1bd7c-e10e-11e7-8b8a-ee9dfca981ed.png">

```
$ python app_runner.py -h
usage: app_runner.py [-h] (--demo DEMO | --files FILES [FILES ...])
                     [--diffs DIFFS [DIFFS ...]] [--heatmap {svg,canvas}]
                     [--top_rows TOP_ROWS] [--cluster_rows] [--cluster_cols]
                     [--colors {Greys,YlGnBu,Greens,YlOrRd,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,Hot,Blackbody,Earth,Electric,Viridis}]
                     [--reverse_colors] [--html_error]
                     [--api_prefix API_PREFIX] [--debug] [--port PORT]

Light-weight visualization for differential expression

optional arguments:
  -h, --help            show this help message and exit
  --demo DEMO           Generates random data rather than reading files. The
                        argument determines the dimensions of the random
                        matrix.
  --files FILES [FILES ...]
                        Read CSV or TSV files. Multiple files will be joined
                        based on the values in the first column. Compressed
                        files are also handled, if correct extension is given.
                        (ie ".csv.gz")
  --diffs DIFFS [DIFFS ...]
                        Read CSV or TSV files containing differential analysis
                        data.
  --heatmap {svg,canvas}
                        The canvas-based heatmap will render much more quickly
                        for large data sets, but the image is blurry, rather
                        than having sharp edges; TODO.
  --top_rows TOP_ROWS   For heatmap, sort by row variance, and take the top n.
  --cluster_rows        For heatmap, hierarchically cluster rows.
  --cluster_cols        For heatmap, hierarchically cluster columns.
  --colors {Greys,YlGnBu,Greens,YlOrRd,Bluered,RdBu,Reds,Blues,Picnic,Rainbow,Portland,Jet,Hot,Blackbody,Earth,Electric,Viridis}
                        Color scale for the heatmap.
  --reverse_colors      Reverse the color scale of the heatmap.
  --html_error          If there is a configuration error, instead of exiting,
                        start the server and display an error page.
  --api_prefix API_PREFIX
                        Prefix for API URLs. (This is only useful inside
                        Refinery.)
  --debug               Runs the underlying Flask server in debug mode, and
                        makes some of the internals visible on the page.
  --port PORT
```

## Getting Started

The best way to run the app during development is just as a Flask app.
Check out the project, set up a virtualenv and install dependencies:
```bash
$ git clone https://github.com/mccalluc/heatmap-scatter-dash.git
$ cd heatmap-scatter-dash
  # Set up a virtualenv, and then install dependencies:
$ pip install -r context/requirements.txt
```

Then try one of these:

```bash
$ cd context

  # Generate a random matrix:
$ python app_runner.py --demo 1,10,10 --port 8888

  # Load data from disk:
$ python app_runner.py --files ../fixtures/good/data/counts.csv --diffs ../fixtures/good/data/stats-* --port 8888

  # Read an input.json like that created by Refinery:
$ python app_runner_refinery.py --input ../fixtures/good/input.json --port 8888
```

and visit `http://localhost:8888/`.

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

## Notes

There are a few [notes](docs) on implementation decisions and lessons learned.
