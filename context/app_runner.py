#!/usr/bin/env python
import argparse
import html
import traceback
from os import makedirs
from os.path import abspath, basename
from warnings import warn

import numpy as np
import pandas
from flask import Flask, send_from_directory
from werkzeug.contrib.profiler import ProfilerMiddleware

from app.download.download_app import DownloadApp
from app.help.help_app import HelpApp
from app.utils import tabular
from app.utils.frames import find_index, merge
from app.utils.vulcanize import vulcanize
from app.vis.callbacks import VisCallbacks


def file_dataframes(files):
    frames = []
    for file in files:
        df = tabular.parse(file)
        df.index = [str(i) for i in df.index]
        frames.append(df)
        file.close()
    return frames


def demo_dataframes(rows, cols, metas):
    data_array = np.random.rand(rows, cols)
    cond_labels = ['cond-{}'.format(i) for i in range(cols)]
    gene_labels = ['gene-{}'.format(i) for i in range(rows)]

    meta_array = np.random.rand(cols, metas)
    meta_labels = ['meta-{}'.format(i) for i in range(metas)]
    return (
        [pandas.DataFrame(data_array, columns=cond_labels, index=gene_labels)],
        [pandas.DataFrame(meta_array, columns=meta_labels, index=cond_labels)]
    )


def init(args, parser):  # TODO: Why is parser here?
    if args.files:
        dataframes = file_dataframes(args.files)
        meta_dataframes = file_dataframes(args.metas)
    elif args.demo:
        (dataframes, meta_dataframes) = demo_dataframes(*args.demo)
    else:
        # Argparser validation should keep us from reaching this point.
        raise Exception('Either "demo" or "files" is required')

    union_dataframe = merge(dataframes)
    genes = set(union_dataframe.index.tolist())
    if args.diffs:
        diff_dataframes = {}
        for diff_file in args.diffs:
            diff_dataframe = tabular.parse(
                diff_file,
                col_zero_index=False,
                keep_strings=True
            )
            key = basename(diff_file.name)
            value = vulcanize(find_index(diff_dataframe, genes))
            diff_dataframes[key] = value
    else:
        diff_dataframes = {
            'No differential files given': pandas.DataFrame()
        }

    union_meta_dataframe = merge(meta_dataframes)

    server = Flask(__name__, static_url_path='')

    server.route('/static/<path:path>')(
        lambda path: send_from_directory('app/static', path)
    )

    # TODO: Just calling constructor shouldn't do stuff.
    VisCallbacks(
        server=server,
        url_base_pathname='/',
        union_dataframe=union_dataframe,
        diff_dataframes=diff_dataframes,
        meta_dataframe=union_meta_dataframe,
        api_prefix=args.api_prefix,
        debug=args.debug,
        most_variable_rows=args.most_variable_rows,
        html_table=args.html_table,
        truncate_table=args.truncate_table
    )
    HelpApp(
        server=server,
        url_base_pathname='/help',
    )
    DownloadApp(
        server=server,
        url_base_pathname='/download',
        dataframe=union_dataframe
    )
    return server


def main(args, parser=None):
    try:
        app = init(args=args, parser=parser)
        if args.profile:
            abs_profile_path = abspath(args.profile)
            makedirs(abs_profile_path, exist_ok=True)
            app.wsgi_app = ProfilerMiddleware(app.wsgi_app,
                                              profile_dir=abs_profile_path)
        app.run(
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
            raise Exception(e)
        app = Flask('error-page')

        args_str = str(args)
        warn(args_str)

        error_str = ''.join(
            traceback.TracebackException.from_exception(e).format()
        )
        warn(error_str)

        @app.route("/")
        def error_page():
            return '''
                <html><head><title>Error</title></head><body>
                <p>An error has occurred: There may be a problem with the
                input provided. To report a bug, please copy this page and
                paste it in a <a href="{url}">bug report</a>. Thanks!</p>
                <pre>{args}</pre>
                <pre>{stack}</pre>
                </body></html>'''.format(
                url='https://github.com/refinery-platform/'
                'heatmap-scatter-dash/issues',
                args=html.escape(args_str),
                stack=html.escape(error_str))

        app.run(
            port=args.port,
            host='0.0.0.0'
        )


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Light-weight visualization for differential expression')

    binary_file = argparse.FileType('rb')
    input_source = parser.add_mutually_exclusive_group(required=True)
    input_source.add_argument(
        '--demo', nargs=3, type=int, metavar=('ROWS', 'COLS', 'META'),
        help='Generates a random matrix with the number of rows and columns '
             'specified. In addition, "META" determines the number of mock '
             'metadata fields to associate with each column.')
    input_source.add_argument(
        '--files', nargs='+', metavar='CSV', type=binary_file,
        help='Read CSV or TSV files. Identifiers should be in the first '
             'column and multiple files will be joined on identifier. '
             'Gzip and Zip files are also handled.')

    parser.add_argument(
        '--diffs', nargs='+', metavar='CSV',
        type=binary_file, default=(),
        help='Read CSV or TSV files containing differential expression data.')

    parser.add_argument(
        '--metas', nargs='+', metavar='CSV',
        type=binary_file, default=(),
        help='Read CSV or TSV files containing metadata: Row labels should '
             'match column headers of the raw data.')

    parser.add_argument(
        '--most_variable_rows', type=int, default=500, metavar='ROWS',
        help='For the heatmap, we first sort by row variance, and then take '
             'the number of rows specified here. Defaults to 500.')

    parser.add_argument(
        '--html_table', action='store_true',
        help='The default is to use pre-formatted text for the tables. '
             'HTML tables are available, but are twice as slow.')

    parser.add_argument(
        '--truncate_table', type=int, default=None, metavar='N',
        help='Truncate the table to the first N rows. Table rendering is '
             'often a bottleneck. Default is not to truncate.')

    parser.add_argument(
        '--port', type=int, default=8050,
        help='Specify a port to run the server on. Defaults to 8050.')

    group = parser.add_argument_group(
        'Refinery/Developer',
        'These parameters will probably only be of interest to developers, '
        'and/or they are used when the tool is embedded in Refinery.')

    group.add_argument(
        '--profile', nargs='?', type=str, default='/tmp', metavar='DIR',
        help='Saves a profile for each request in the specified directory, '
             '"/tmp" by default. Profiles can be viewed with snakeviz.')
    group.add_argument(
        '--html_error', action='store_true',
        help='If there is a configuration error, instead of exiting, '
             'start the server and display an error page.')
    group.add_argument(
        '--debug', action='store_true',
        help='Run the server in debug mode: The server will '
             'restart in response to any code changes, '
             'and some hidden fields will be shown.')
    group.add_argument(
        '--api_prefix', default='', metavar='PREFIX',
        help='Prefix for API URLs.')

    return parser


if __name__ == '__main__':
    parser = arg_parser()
    args = parser.parse_args()
    main(args, parser)
