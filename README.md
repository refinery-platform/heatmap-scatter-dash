# heatmap-scatter-dash

A heatmap-scatterplot (TODO: -pca-volcano) using [Dash by plotly](https://plot.ly/products/dash/).
Can be run as a Flask app from the commandline,
or as Docker container for [Refinery](https://github.com/refinery-platform/refinery-platform) visualizations.

## Development

The best way to run the app during develoment is just as a Flask app.
Read [`.travis.yml`](.travis.yml) for instructions on installing dependencies. Then:

```bash
$ python context/app/app_runner.py --demo
```

To build and run the Docker container:

```bash
$ docker build --tag heatmap-scatter-dash context
$ 
```