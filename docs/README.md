Notes on some of the implementation choices in this app:

- Hierarchical clustering is a potentially slow process. [This notebook](cluster_profiling.ipynb) can give us a rough sense
of how the execution time increases with larger arrays.
- After trying to find a clear way of having the various cross filters work together, we ultimately decided that the last
user interaction is the one that should count. This is not the usual pattern in Dash, but [here's](event_timestamps_demo_app.py)
a simple demo of the scheme.
- I've come to believe that *quick-startup* and *scalability* are contradictory requirements.
[Here's](quick-start-scale.md) an explanation why, and a map of some of the ways forward.
