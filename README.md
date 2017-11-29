# heatmap-scatter-dash

A heatmap-scatterplot (TODO: -pca-volcano) using [Dash by plotly](https://plot.ly/products/dash/).
Can be run as a flask app from the commandline,
or as Docker container for [Refinery](https://github.com/refinery-platform/refinery-platform) visualizations.

## Development

Read [`.travis.yml`](.travis.yml) for instructions on installing dependencies. Then:

```bash
$ python context/app/app_runner.py --demo
```