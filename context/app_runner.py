#!/usr/bin/env python
import argparse
import re
from sys import exit

import numpy as np
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.app_callbacks import AppCallbacks

from app.utils.cluster import cluster
from app.utils.frames import merge, reindex
from os.path import basename


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


def file_dataframes(files):
    return [
        pandas.read_csv(file, index_col=0)
        for file in files
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


def main(args, parser=None):
    if args.files:
        dataframes = file_dataframes(args.files)
    elif args.demo:
        dataframes = demo_dataframes(**args.demo)
    else:
        message = 'Either "--demo FRAMES,ROWS,COLS" '\
                  'or "--files FILE" is required'
        if parser:
            print(message)
            parser.print_help()
            exit(1)
        else:
            raise Exception(message)

    dataframe = cluster(
        merge(dataframes),
        skip_zero=args.skip_zero,
        cluster_rows=args.cluster_rows,
        cluster_cols=args.cluster_cols)

    keys = set(dataframe.index.tolist())
    diff_dataframes = {
        basename(handle.name): reindex(pandas.read_csv(handle), keys)
        for handle in args.diffs
    }

    AppCallbacks(
        dataframe=dataframe,
        diff_dataframes=diff_dataframes,
        colors=args.colors,
        heatmap_type=args.heatmap
    ).app.run_server(
        debug=args.debug,
        port=args.port,
        host='0.0.0.0'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Light-weight visualization for differential expression')

    input_source = parser.add_mutually_exclusive_group(required=True)
    input_source.add_argument(
        '--demo', type=dimensions_regex,
        help='Generates random data rather than reading files. '
        'The argument determines the dimensions of the random matrix.')
    input_source.add_argument(
        '--files', nargs='+', type=argparse.FileType('r'),
        help='Read CSV files. Multiple files will be joined '
             'based on the values in the first column')

    parser.add_argument(
        '--diffs', nargs='+', type=argparse.FileType('r'), default=[],
        help='Read CSV files containing differential analysis data.')

    parser.add_argument(
        '--heatmap', choices=['svg', 'canvas'], required=True,
        help='The canvas-based heatmap will render much more quickly '
        'for large data sets, but the image is blurry, '
        'rather than having sharp edges. TODO.')
    parser.add_argument(
        '--skip_zero', action='store_true',
        help='Rows in the CSV which are all zero will be skipped.')

    parser.add_argument(
        '--cluster_rows', action='store_true',
        help='Hierarchically cluster rows')
    parser.add_argument(
        '--cluster_cols', action='store_true',
        help='Hierarchically cluster columns')
    parser.add_argument(
        '--colors', choices=list(PLOTLY_SCALES), default='Greys',
        help='Color scale for the heatmap')

    parser.add_argument('--port', type=int, default=8050)
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()
    main(args, parser)
