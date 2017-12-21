#!/usr/bin/env python
import argparse
import re
from os.path import basename

import numpy as np
import pandas
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.app_callbacks import AppCallbacks
from app.utils.cluster import cluster
from app.utils.frames import find_index, merge, sort_by_variance
from app.utils.vulcanize import vulcanize


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
        pandas.read_csv(file, index_col=0, sep=None, engine='python')
        # With sep=None, csv.Sniffer is used to detect filetype.
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
        # Argparser validation should keep us from reaching this point.
        raise Exception('Either "demo" or "files" is required')

    merged = merge(dataframes)
    if args.top:
        merged = sort_by_variance(merged).head(args.top)

    dataframe = cluster(
        merged,
        cluster_rows=args.cluster_rows,
        cluster_cols=args.cluster_cols)

    keys = set(dataframe.index.tolist())
    if args.diffs:
        diff_dataframes = {
            # app_runner and refinery pass different things in here...
            # TODO:  Get rid of "if / else"
            basename(file.name if hasattr(file, 'name') else file):
                vulcanize(find_index(pandas.read_csv(file), keys,
                                     drop_unmatched=args.scatterplot_top))
            for file in args.diffs
        }
    else:
        diff_dataframes = {
            'No differential files given': pandas.DataFrame()
        }

    AppCallbacks(
        dataframe=dataframe,
        diff_dataframes=diff_dataframes,
        colors=args.colors,
        reverse_colors=args.reverse_colors,
        heatmap_type=args.heatmap,
        api_prefix=args.api_prefix
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
             'based on the values in the first column. '
             'Compressed files are also handled, '
             'if correct extension is given. (ie ".csv.gz")')

    parser.add_argument(
        '--diffs', nargs='+', type=argparse.FileType('r'), default=[],
        help='Read CSV files containing differential analysis data.')
    # --diffs itself is optional... but if present, files must be given.

    parser.add_argument(
        '--heatmap', choices=['svg', 'canvas'], required=True,
        help='The canvas-based heatmap will render much more quickly '
        'for large data sets, but the image is blurry, '
        'rather than having sharp edges; TODO.')
    parser.add_argument(
        '--top', type=int,
        help='Sort by row variance, descending, and take the top n.')
    parser.add_argument(
        '--scatterplot_top', action='store_true', default=False,
        help='In the scatterplots, show only items corresponding '
        'to rows in the heatmap. (Only used together with --top.)'
    )

    parser.add_argument(
        '--cluster_rows', action='store_true',
        help='Hierarchically cluster rows.')
    parser.add_argument(
        '--cluster_cols', action='store_true',
        help='Hierarchically cluster columns.')

    parser.add_argument(
        '--colors', choices=list(PLOTLY_SCALES), default='Greys',
        help='Color scale for the heatmap.')
    parser.add_argument(
        '--reverse_colors', action='store_true',
        help='Reverse the color scale of the heatmap.')

    parser.add_argument(
        '--api_prefix', default='',
        help='Prefix for API URLs. '
        '(This is only useful inside Refinery.)')

    parser.add_argument('--port', type=int, default=8050)
    parser.add_argument('--debug', action='store_true')

    args = parser.parse_args()
    main(args, parser)
