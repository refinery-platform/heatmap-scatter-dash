from scipy.cluster.hierarchy import leaves_list, linkage

# I found this tutorial very helpful:
# https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/


def _order_rows(dataframe, clustering):
    row_labels = dataframe.index.tolist()
    if clustering and len(row_labels) > 1:
        rows_linkage = linkage(dataframe, 'ward')
        rows_order = leaves_list(rows_linkage).tolist()
        return [row_labels[i] for i in rows_order]
    else:
        return row_labels


def cluster(dataframe, cluster_rows=False, cluster_cols=False):
    '''
    Hierarchically cluster the rows and columns of a DataFrame.

    :param dataframe: pandas DataFrame
    :param cluster_rows: If True, cluster rows: Defaults to False.
    :param cluster_cols: If True, cluster columns: Defaults to False.
    :return: Reordered DataFrame
    '''
    col_label_order = _order_rows(dataframe.T, cluster_cols)
    row_label_order = _order_rows(dataframe, cluster_rows)
    return dataframe[col_label_order].loc[row_label_order]
