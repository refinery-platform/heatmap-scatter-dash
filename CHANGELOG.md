# Change Log

## [v0.1.15](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.15) (Aug 13, 2018)

* Fix race condition where selecting points on the scatterplot did not always
update the found set.
* Also look for "padj" and "fdr" when scanning headers.
* Move help to tab instead of separate page.


## [v0.1.14](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.14) (Aug 2, 2018)

* app_runner_refinery sniffs files to determine if they are counts or differential expression.


## [v0.1.13](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.13) (Jul 26, 2018)

* If the body of the table has non-numeric columns, the value in the first
of those columns is prepended to the row label. (Often, the first column is
just a numeric ID, but something more human-readable is present farther to
the right.)


## [v0.1.12](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.12) (Jul 10, 2018)

* Support inputs with just two columns and numeric gene IDs.


## [v0.1.11](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.11) (Jun 13, 2018)

* By default, drop non-numeric values from dataframe.


## [v0.1.10](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.10) (May 2, 2018)

* Big speedup by using preformatted output rather than html for table.


## [v0.1.9](https://github.com/refinery-platform/heatmap-scatter-dash/tree/v0.1.9) (Apr 30, 2018)

* Support GCT files.
