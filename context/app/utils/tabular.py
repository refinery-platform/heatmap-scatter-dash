from csv import Sniffer

from pandas import read_csv


def parse(file, col_zero_index=True):
    dialect = Sniffer().sniff(file.readline())
    file.seek(0)
    return read_csv(
        file,
        index_col=0 if col_zero_index else None,
        delimiter=dialect.delimiter,
        quotechar=dialect.quotechar,
        # TODO: more?
    )
