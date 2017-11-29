from app_factory import make_app
from sys import argv
import pandas
from io import StringIO


if __name__ != '__main__':
    raise Exception('Should be run as script')

if len(argv) > 2:
    raise Exception('Expects one argument, the csv file to read')

if len(argv) == 2:
    csv = open(argv[1])
else:
    csv = StringIO("""gene,cond1,cond2,cond3,cond4
        gene-one,0.2,0.7,0.2,0.7
        gene-two,0.4,0.8,0.2,0.8
        gene-three,0.5,0.8,0.1,0.9
        gene-four,0.6,0.8,0.3,0.8
        gene-five,0.6,0.9,0.4,0.8
        gene-six,0.6,0.9,0.5,0.8
        """)
dataframe = pandas.read_csv(csv, index_col=0)
make_app(dataframe).run_server(debug=True)
