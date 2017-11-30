import argparse
from io import StringIO
from sys import exit

import numpy as np
import pandas

from app_factory import make_app

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
    dataframe = pandas.read_csv(csv, index_col=0)
else:
    rows = 20
    cols = 10
    array = np.random.rand(rows, cols)
    col_labels = ['cond-{}'.format(i) for i in range(cols)]
    row_labels = ['gene-{}'.format(i) for i in range(rows)]
    dataframe = pandas.DataFrame(array, columns=col_labels, index=row_labels)

make_app(dataframe).run_server(
    debug=args.debug,
    port=int(args.port or '8050'),
    host='0.0.0.0'
)
