import pandas
from sklearn import decomposition


def pca(dataframe, components=2):
    orig_columns = dataframe.columns.tolist()
    pca = decomposition.PCA(n_components=components)

    array = pca.fit_transform(dataframe.T).tolist()
    return pandas.DataFrame(
        array,
        columns=['pc{}'.format(i) for i in range(components)],
        index=orig_columns)
