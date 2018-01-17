This is a tool for exploring tabular gene expression and differential expression data.

### Components

There are three main components:

*Insert screenshot here*

- On the left is a hierarchically clustered heatmap, with a gene search box and an axis toggle.
- To the right and above is a scatter-plot of the conditions in the dataset,
arranged by their principle components.
- To the right and below is a scatter-plot of genes, and in successive tabs,
a volcano plot for differential expression data, and a table of the current active gene set and conditions.

### Tools

Each component offers a tool bar when you hover over it. From left to right:

*Insert small screenshot here*

- Click the camera icon to save the current graph as a PNG.
- Click the disk icon to save the data on the Plotly web service.
- Use the magnifying glass to zoom in on a particular region.
- Use the pan tool to shift the view after you zoom, and to get more information on individual points.
- Use the marquee or lasso to select a subset of points.
- Click the house icon to return to the original view.

### Interaction

Each component is linked to the others in what we hope is a natural way. For example:

- Select a subset in any scatterplot and the rows or columns of the heatmap
will be updated accordingly.
- Select a subset in the volcano plot or the sample-by-sample plot and the other
will be updated accordingly.
- Change the axes of the sample-by-sample plot, and the corresponding dots of the 
PCA scatterplot will be highlighted.
- Selecting a logarithmic scale for the heatmap will also update the axes of the
sample-by-sample plot.

### Limitations

- When working with more than 10,000 genes, certain actions may begin to take longer,
although there is no hard-coded limit.
- It is not currently possible to select a range on the heatmap, and have the scatterplots update accordingly

## Feedback

Please make any feature requests or bug reports [here](https://github.com/refinery-platform/heatmap-scatter-dash/issues/new).

