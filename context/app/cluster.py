from scipy.cluster.hierarchy import dendrogram, linkage, leaves_list
import numpy as np

# I found this tutorial very helpful:
# https://joernhees.de/blog/2015/08/26/scipy-hierarchical-clustering-and-dendrogram-tutorial/

def cluster(dataframe):
    cols_linkage = linkage(dataframe.T, 'ward')
    cols_order = leaves_list(cols_linkage).tolist()

    rows_linkage = linkage(dataframe, 'ward')
    rows_order = leaves_list(rows_linkage).tolist()

    return dataframe[cols_order].iloc[rows_order]
