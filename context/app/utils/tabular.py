from pandas import read_csv

def parse(file):
    # TODO: Read TSV, and test
    return read_csv(file, index_col=0, sep=',')