import argparse
import re
from sys import exit

import numpy as np
import pandas

from app_factory import make_app

if __name__ != '__main__':
    raise Exception('Should be run as script')


def dimensions_regex(s, pattern=re.compile(r"\d+,\d+,\d+")):
    if not pattern.match(s):
        raise argparse.ArgumentTypeError(
            'Should be of the form "FRAMES,ROWS,COLS", '
            'where each is an integer'
        )
    dimensions = [int(i) for i in s.split(',')]
    return {
        'frames': dimensions[0],
        'rows': dimensions[1],
        'cols': dimensions[2]
    }


def real_dataframes(files):
    return [
        pandas.read_csv(file, index_col=0)
        for file in args.files
    ]


def demo_dataframes(frames, rows, cols):
    dataframes = []
    for f in range(frames):
        array = np.random.rand(rows, cols)
        col_labels = ['cond-{}'.format(i + f * cols // 3)
                      for i in range(cols)]
        row_labels = ['gene-{}'.format(i + f * rows // 3)
                      for i in range(rows)]
        dataframes.append(pandas.DataFrame(array,
                                           columns=col_labels,
                                           index=row_labels))
    return dataframes


parser = argparse.ArgumentParser(description='Plotly Dash visualization')
parser.add_argument('--demo', type=dimensions_regex)
parser.add_argument('--files', nargs='+', type=argparse.FileType('r'))
parser.add_argument('--port', type=int, default=8050)
parser.add_argument('--debug', action='store_true')
parser.add_argument('--cluster', action='store_true')
args = parser.parse_args()


if args.files:
    dataframes = real_dataframes(args.files)
elif args.demo:
    dataframes = demo_dataframes(**args.demo)
else:
    print('Either "--demo FRAMES,ROWS,COLS" or "--files FILE" is required')
    parser.print_help()
    exit(1)


merged_df = pandas.DataFrame()
for frame in dataframes:
    merged_df = merged_df.merge(frame,
                                how='outer',
                                right_index=True,
                                left_index=True)
make_app(merged_df, clustering=args.cluster).run_server(
    debug=args.debug,
    port=args.port,
    host='0.0.0.0'
)
