import argparse
import re
from sys import exit

import numpy as np
import pandas

from app.app_wrapper import AppWrapper
from app.data_frame_merge import DataFrameMerge


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
    if (args.demo_counts and args.diffs) or \
        (args.counts and args.demo_diffs):
        raise Exception('Demo data and real data should not be used together')
        # Argument groups are not designed for nesting;
        # Argparse can't do this for us.
        # https://bugs.python.org/issue26952#msg265164

    if args.counts:
        count_frames = real_dataframes(args.counts)
    elif args.demo_counts:
        count_frames = demo_dataframes(**args.demo_counts)
    else:
        raise Exception('Argparse validation should have failed earlier')

    if args.diffs:
        diff_frames = real_dataframes(args.diffs)
    elif args.demo_diffs:
        diff_frames = demo_dataframes(**args.demo_diffs)
    else:
        diff_frames = []

    df_merge = DataFrameMerge(
        count_frames=count_frames,
        diff_frames=diff_frames,
        cluster=args.cluster)

    AppWrapper(df_merge).app.run_server(
        debug=args.debug,
        port=args.port,
        host='0.0.0.0'
    )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Plotly Dash visualization',
        epilog='Arguments to --demo_counts and --demo_diffs should be of the form "FRAMES,ROWS,COLS".'
    )

    counts_source = parser.add_mutually_exclusive_group(required=True)
    counts_source.add_argument('--demo_counts', type=dimensions_regex)
    counts_source.add_argument('--counts', nargs='+',
                              type=argparse.FileType('r'))

    diffs_source = parser.add_mutually_exclusive_group()
    diffs_source.add_argument('--demo_diffs', type=dimensions_regex)
    diffs_source.add_argument('--diffs', nargs='+',
                               type=argparse.FileType('r'))

    parser.add_argument('--port', type=int, default=8050)
    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--cluster', action='store_true')
    args = parser.parse_args()
    main(args, parser)
