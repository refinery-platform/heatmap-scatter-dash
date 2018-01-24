import warnings
from csv import Sniffer

from pandas import read_csv


def parse(file, col_zero_index=True):
    # We could use read_csv with separator=None...
    # but that requires the python parser, which seems to be about
    # three times as slow as the c parser.
    dialect = Sniffer().sniff(file.readline())
    file.seek(0)
    with warnings.catch_warnings():
        # https://github.com/pandas-dev/pandas/issues/18845
        # pandas raises unnecessary warnings.
        warnings.simplefilter("ignore")
        dataframe = read_csv(
            file,
            index_col=0 if col_zero_index else None,
            dialect=dialect
        )
    return dataframe
