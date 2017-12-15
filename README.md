# heatmap-scatter-dash

A heatmap-scatterplot using [Dash by plotly](https://plot.ly/products/dash/).
Can be run as a Flask app from the commandline,
or as Docker container for [Refinery](https://github.com/refinery-platform/refinery-platform) visualizations.

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
$ python app_runner.py --demo 1,10,10 --port 8888 --cluster

  # Load data from disk:
$ python app_runner.py --files fixtures/good/data/* --port 8888 --cluster

  # Read an input.json like that created by Refinery:
$ python app_runner_refinery.py --input fixtures/good/input.json --port 8888
```

and visit `http://localhost:8888/`.

## Testing

One bash script, `test.sh`, handles all our tests:
- Python unit tests
- Python style tests (`flake8` and `isort`)
- Cypress.io interaction tests
- Docker container build and launch

A few more dependencies are required for this to work locally:
```
  # Install Docker: https://www.docker.com/community-edition
$ pip install -r requirements-dev.txt
$ npm install cypress --save-dev
```

## Release

Successful Github tags and PRs will prompt Travis to push the built image to Dockerhub. For a new version number:

```bash
$ git tag v0.0.x && git push origin --tags
```