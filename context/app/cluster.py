from scipy.cluster.hierarchy import dendrogram, linkage, leaves_list
import numpy as np

# I found this tutorial very helpful:
# https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/

def cluster(dataframe):
    cols_linkage = linkage(dataframe.T, 'ward')
    cols_order = leaves_list(cols_linkage).tolist()
    col_labels = dataframe.columns.tolist()
    col_label_order = [col_labels[i] for i in cols_order]

    rows_linkage = linkage(dataframe, 'ward')
    rows_order = leaves_list(rows_linkage).tolist()
    row_labels = dataframe.index.tolist()
    row_label_order = [row_labels[i] for i in rows_order]

    return dataframe[col_label_order].loc[row_label_order]
