#!/usr/bin/env python
import argparse
import html
import re
import traceback
from os.path import basename
from warnings import warn

import numpy as np
import pandas
from flask import Flask
from plotly.figure_factory.utils import PLOTLY_SCALES

from app.help.help_app import HelpApp
from app.utils import tabular
from app.utils.frames import find_index, merge
from app.utils.vulcanize import vulcanize
from app.vis.callbacks import VisCallbacks


def dimensions_regex(s, pattern=re.compile(r"\d+,\d+")):
    if not pattern.match(s):
        raise argparse.ArgumentTypeError(
            'Should be of the form "ROWS,COLS", '
            'where each is an integer'
        )
    dimensions = [int(i) for i in s.split(',')]
    return {
        'rows': dimensions[0],
        'cols': dimensions[1]
    }


def file_dataframes(files):
    return [
        tabular.parse(file) for file in files
    ]


def demo_dataframes(rows, cols):
    array = np.random.rand(rows, cols)
    col_labels = ['cond-{}'.format(i) for i in range(cols)]
    row_labels = ['gene-{}'.format(i) for i in range(rows)]
    return [pandas.DataFrame(array,
                             columns=col_labels,
                             index=row_labels)]


def main(args, parser=None):
    try:
        if args.files:
            dataframes = file_dataframes(args.files)
        elif args.demo:
            dataframes = demo_dataframes(*args.demo)
        else:
            # Argparser validation should keep us from reaching this point.
            raise Exception('Either "demo" or "files" is required')

        union_dataframe = merge(dataframes)
        genes = set(union_dataframe.index.tolist())
        if args.diffs:
            diff_dataframes = {}
            for diff_file in args.diffs:
                diff_dataframe = tabular.parse(diff_file)
                # app_runner and refinery pass different things in here...
                # TODO:  Get rid of "if / else"
                key = basename(diff_file.name
                               if hasattr(diff_file, 'name')
                               else diff_file)
                value = vulcanize(find_index(diff_dataframe, genes))
                diff_dataframes[key] = value
        else:
            diff_dataframes = {
                'No differential files given': pandas.DataFrame()
            }

        server = Flask('heatmap-scatter-dash')

        # TODO: Just calling constructor shouldn't do stuff.
        VisCallbacks(
            server=server,
            url_base_pathname='/',
            union_dataframe=union_dataframe,
            diff_dataframes=diff_dataframes,
            colors=args.colors,
            reverse_colors=args.reverse_colors,
            api_prefix=args.api_prefix,
            debug=args.debug,
            most_variable_rows=args.most_variable_rows,
            cluster_rows=args.cluster_rows,
            cluster_cols=args.cluster_cols
        )
        HelpApp(
            server=server,
            url_base_pathname='/help',
        )

        server.run(
            debug=args.debug,
            port=args.port,
            host='0.0.0.0'
        )
    except Exception as e:
        # Big try-blocks are usually to be avoided...
        # but here, we want to be sure that some server comes up
        # and returns a 200, so that django-proxy knows to stop waiting,
        # and the end-user can see the error.
        if not args.html_error:
            raise
        app = Flask('error-page')
        error_str = ''.join(
            traceback.TracebackException.from_exception(e).format()
        )
        warn(error_str)

        @app.route("/")
        def error_page():
            return (
                '<html><head><title>error</title></head><body><pre>' +
                html.escape(error_str) +
                '</pre></body></html>')
        app.run(
            port=args.port,
            host='0.0.0.0'
        )


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Light-weight visualization for differential expression')

    input_source = parser.add_mutually_exclusive_group(required=True)
    input_source.add_argument(
        '--demo', nargs=2, type=int, metavar=('ROWS', 'COLS'),
        help='Generates a random matrix with the rows and columns specified.')
    input_source.add_argument(
        '--files', nargs='+', metavar='CSV', type=argparse.FileType('r'),
        help='Read CSV or TSV files. Identifiers should be in the first '
             'column and multiple files will be joined on identifier. '
             'Compressed files are also handled, '
             'if correct extension is given. (ie ".csv.gz")')

    parser.add_argument(
        '--diffs', nargs='+', metavar='CSV',
        type=argparse.FileType('r'), default=[],
        help='Read CSV or TSV files containing differential expression data.')

    parser.add_argument(
        '--most_variable_rows', type=int, default=500, metavar='ROWS',
        help='For the heatmap, we first sort by row variance, and then take '
             'the number of rows specified here. Defaults to 500.')

    parser.add_argument(
        '--cluster_rows', action='store_true',
        help='For the heatmap, hierarchically cluster rows.')
    parser.add_argument(
        '--cluster_cols', action='store_true',
        help='For the heatmap, hierarchically cluster columns.')

    parser.add_argument(
        '--colors', choices=list(PLOTLY_SCALES), default='Greys',
        help='Color scale for the heatmap. Defaults to grey scale.')
    parser.add_argument(
        '--reverse_colors', action='store_true',
        help='Reverse the color scale of the heatmap.')

    parser.add_argument(
        '--html_error', action='store_true',
        help='If there is a configuration error, instead of exiting, '
        'start the server and display an error page. '
        '(This is used by Refinery.)')
    parser.add_argument(
        '--api_prefix', default='', metavar='PREFIX',
        help='Prefix for API URLs. '
        '(This is used by Refinery.)')
    parser.add_argument(
        '--debug', action='store_true',
        help='Run the server in debug mode: The server will '
        'restart in response to any code changes, '
        'and some hidden fields will be shown.')
    parser.add_argument(
        '--port', type=int, default=8050,
        help='Specify a port to run the server on. Defaults to 8050.')

    args = parser.parse_args()
    main(args, parser)
