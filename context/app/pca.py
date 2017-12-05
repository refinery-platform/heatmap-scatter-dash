import pandas
from sklearn import decomposition


def pca(dataframe, components=4):
    # TODO: Confirm that this is a good number of components
    dataframe = dataframe.fillna(0)  # TODO: Confirm that this is correct
    orig_columns = dataframe.columns.tolist()
    components = min(components, len(orig_columns))
    pca = decomposition.PCA(n_components=components)

    array = pca.fit_transform(dataframe.T).tolist()
    return pandas.DataFrame(
        array,
        columns=['pc{}'.format(i) for i in range(components)],
        index=orig_columns)
