# heatmap-scatter-dash

A heatmap-scatterplot (TODO: -pca-volcano) using [Dash by plotly](https://plot.ly/products/dash/).
Can be run as a Flask app from the commandline,
or as Docker container for [Refinery](https://github.com/refinery-platform/refinery-platform) visualizations.

## Development

The best way to run the app during development is just as a Flask app.
Read [`.travis.yml`](.travis.yml) for instructions on installing dependencies. 
(You probably want a virtualenv.) Then:

```bash
$ PYTHONPATH=context python context/app_runner.py --demo 1,10,10 --port 8888 --cluster
```

and visit `http://localhost:8888/`.

To build and run the Docker container:

```bash
$ docker build --tag heatmap-scatter-dash context
$ docker run --detach --publish 8889:80 heatmap-scatter-dash
```

Then visit `http://localhost:8889/`.

## Release

Successful Github tags and PRs will prompt Travis to push the built image to Dockerhub. For a new version number:

```bash
$ git tag v0.0.x && git push origin --tags
```