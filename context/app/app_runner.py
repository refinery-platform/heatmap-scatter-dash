import argparse
from sys import exit

import numpy as np
import pandas

import re

from app_factory import make_app

if __name__ != '__main__':
    raise Exception('Should be run as script')

def dimensions_regex(s, pattern=re.compile(r"\d+,\d+,\d+")):
    if not pattern.match(s):
        raise argparse.ArgumentTypeError(
            'Should be of the form "FRAMES,ROWS,COLS", where each is an integer'
        )
    return [int(i) for i in s.split(',')]

parser = argparse.ArgumentParser(description='Plotly Dash visualization')
parser.add_argument('--demo', type=dimensions_regex)
parser.add_argument('--port', type=int)
parser.add_argument('--files', nargs='+', type=argparse.FileType('r'))
parser.add_argument('--debug', action='store_true')

args = parser.parse_args()

if not(args.demo or args.file):
    print('Either "--demo" or "--files FILE" is required')
    parser.print_help()
    exit(1)

if args.files:
    dataframes = [
        pandas.read_csv(open(file), index_col=0)
        for file in args.files
    ]
else:
    frames = args.demo[0]
    rows = args.demo[1]
    cols = args.demo[2]
    dataframes = []
    for f in range(frames):
        array = np.random.rand(rows, cols)
        col_labels = ['cond-{}'.format(i + f * cols // 3) for i in range(cols)]
        row_labels = ['gene-{}'.format(i + f * rows // 3) for i in range(rows)]
        dataframes.append(pandas.DataFrame(array, columns=col_labels, index=row_labels))

merged_df = pandas.DataFrame()
for frame in dataframes:
    merged_df = merged_df.merge(frame, how='outer', right_index=True, left_index=True)
make_app(merged_df).run_server(
    debug=args.debug,
    port=int(args.port or '8050'),
    host='0.0.0.0'
)
