from pandas import read_csv


def parse(file, col_zero_index=True):
    index_col = 0 if col_zero_index else None
    return read_csv(file, index_col=index_col, sep=None, engine='python')
