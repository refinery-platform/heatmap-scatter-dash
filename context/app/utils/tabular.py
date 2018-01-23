from pandas import read_csv
from csv import Sniffer


def parse(file_path, col_zero_index=True):
    with open(file_path) as file_handle:
        dialect = Sniffer().sniff(file_handle.readline())
    return read_csv(
        file_path,
        index_col=0 if col_zero_index else None,
        delimiter=dialect.delimiter,
        quotechar=dialect.quotechar,
        # TODO: more?
    )
