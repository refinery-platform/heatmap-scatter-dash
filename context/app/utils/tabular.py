import warnings
from csv import Sniffer

from pandas import read_csv


def parse(file, col_zero_index=True):
    two_bytes = file.read(2)
    file.seek(0)
    index_col = 0 if col_zero_index else None
    if (two_bytes == b'\x1f\x8b'):
        # TODO: Both zip and gzip reading will be slow because
        # internally the python parser is used... but for now this
        # seems better than unzipping to sniff the first line
        dataframe = read_csv(
            file,
            index_col=index_col,
            compression = 'gzip'
        )
    elif (two_bytes == b'\x50\x4b'):  # There are variants in bytes 3 and 4.
        dataframe = read_csv(
            file,
            index_col=index_col,
            compression='zip'
        )
    else:
        # We could use read_csv with separator=None...
        # but that requires the python parser, which seems to be about
        # three times as slow as the c parser.
        first_line = str(file.readline())
        dialect = Sniffer().sniff(first_line)
        # print('"{}" -> "{}"'.format(first_line, dialect.delimiter))
        file.seek(0)
        with warnings.catch_warnings():
            # https://github.com/pandas-dev/pandas/issues/18845
            # pandas raises unnecessary warnings.
            warnings.simplefilter("ignore")
            dataframe = read_csv(
                file,
                index_col=index_col,
                dialect=dialect
            )
    return dataframe
