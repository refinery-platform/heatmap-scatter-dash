from app_factory import make_app
from sys import argv
import pandas

if __name__ != '__main__':
    raise Exception('Should be run as script')

if len(argv) != 2:
    raise Exception('Expects one argument, the csv file to read')

csv = open(argv[1])
dataframe = pandas.read_csv(csv, index_col=0)
make_app(dataframe).run_server(debug=True)
