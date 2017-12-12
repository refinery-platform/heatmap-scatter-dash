from scipy.cluster.hierarchy import leaves_list, linkage

# I found this tutorial very helpful:
# https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/


def _order_rows(dataframe, clustering):
    row_labels = dataframe.index.tolist()
    if clustering:
        rows_linkage = linkage(dataframe, 'ward')
        rows_order = leaves_list(rows_linkage).tolist()
        return [row_labels[i] for i in rows_order]
    else:
        return row_labels


def cluster(dataframe, cluster_rows=False, cluster_cols=False):
    col_label_order = _order_rows(dataframe.T, cluster_cols)
    row_label_order = _order_rows(dataframe, cluster_rows)
    return dataframe[col_label_order].loc[row_label_order]
