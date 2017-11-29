from app_factory import make_app
import pandas
from io import StringIO
import argparse
from sys import exit


if __name__ != '__main__':
    raise Exception('Should be run as script')

parser = argparse.ArgumentParser(description='Plotly Dash visualization')
parser.add_argument('--demo', action='store_true')
parser.add_argument('--port')
parser.add_argument('--file')
parser.add_argument('--debug', action='store_true')

args = parser.parse_args()

if not(args.demo or args.file):
    print('Either "--demo" or "--file FILE" is required')
    parser.print_help()
    exit(1)

if args.file:
    csv = open(args.file)
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
make_app(dataframe).run_server(debug=args.debug, port=int(args.port))
