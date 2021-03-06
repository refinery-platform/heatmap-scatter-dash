#!/usr/bin/env python
import argparse
import html
import json
import os
import re
import traceback
from http.server import HTTPServer, SimpleHTTPRequestHandler
from tempfile import mkdtemp
from urllib.parse import urlparse
from warnings import warn

import requests
from dataframer import dataframer

import app_runner


class RunnerArgs():
    """
    Initialized with an args object for app_runner_refinery.py,
    produces an args object for app_runner.py
    """

    def __init__(self, refinery_args):
        defaults = app_runner.arg_parser().parse_args(
            ['--demo', '1', '1', '1']
        )
        # We clobber the '--demo' setting just below.
        # This seemed more clear than reading the JSON first,
        # getting the files from it, and then passing them through parse_args,
        # but I could be wrong.
        for k, v in vars(defaults).items():
            setattr(self, k, v)
        self.demo = False
        self.http_error = True
        self.port = refinery_args.port
        self.truncate_table = 100

        input_json = self._get_input_json(refinery_args.input)
        if input_json:
            print('input_json:' + input_json)
            input_data = json.loads(input_json)
            parameters = {
                p['name']: p['value'] for p in input_data['parameters']
            }
            assert len(parameters) == 0

            self.api_prefix = input_data['api_prefix']
            assert type(self.api_prefix) == str

            data_directory = input_data['extra_directories'][0]
            file_urls = input_data['file_relationships']
        else:
            data_directory = os.environ.get('DATA_DIR', '/tmp')
            file_urls = _split_envvar('FILE_URLS')
        try:
            mystery_files = _download_files(file_urls, data_directory)
            self.files = []
            self.diffs = []
            for file in mystery_files:
                df = dataframer.parse(file).data_frame
                file.seek(0)  # Reset cursor we can re-read the file.
                if (_column_matches_re(df, app_runner.P_VALUE_RE_LIST) and
                        _column_matches_re(df, app_runner.LOG_FOLD_RE_LIST)):
                    self.diffs.append(file)
                else:
                    self.files.append(file)
        except OSError as e:
            raise Exception('Does {} exist?'.format(data_directory)) from e

    def _get_input_json(self, possible_input_file):
        '''
        Checks three possible sources for JSON input,
        and returns JSON string if found.
        Returns None if all three fail.
        '''
        if possible_input_file and os.path.isfile(possible_input_file):
            return open(possible_input_file, 'r').read(None)

        json = os.environ.get('INPUT_JSON')
        if json:
            return json

        url = os.environ.get('INPUT_JSON_URL')
        if url:
            print('url: ' + url)
            return requests.get(url).text

        return None

    def __repr__(self):
        return '\n'.join(
            ['{}: {}'.format(k, v) for k, v in vars(self).items()]
        )


def _column_matches_re(dataframe, patterns):
    return any(
        re.search(pattern, col, flags=re.IGNORECASE)
        for col in dataframe.columns for pattern in patterns)


def _split_envvar(name):
    value = os.environ.get(name)
    return re.split(r'\s+', value) if value else []


def _download_files(urls, data_dir):
    """
    Given a list of urls and a target directory,
    download the files to the target, and return a list of file handles.
    """
    files = []

    for url in urls:
        parsed = urlparse(url)
        if parsed.scheme == 'file':
            url_path_root = os.path.split(parsed.path)[0]
            abs_data_dir = os.path.abspath(data_dir)
            assert url_path_root == abs_data_dir, \
                '{} != {}'.format(url_path_root, abs_data_dir)
            # The file is already in the right place: no need to move it
            files.append(open(parsed.path))
            continue
        try:
            # Streaming GET for potentially large files
            response = requests.get(url, stream=True)
        except requests.exceptions.RequestException as e:
            raise Exception(
                "Error fetching {} : {}".format(url, e)
            )
        else:
            name = os.path.split(parsed.path)[-1]
            path = os.path.join(data_dir, name)
            with open(path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    # filter out KEEP-ALIVE new chunks
                    if chunk:
                        f.write(chunk)
            files.append(open(path, 'rb'))
            response.close()
    return files


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Webapp for visualizing differential expression')
    parser.add_argument('--input', type=str, required=True,
                        # Because it's a "str" rather than "file",
                        # does not require file to exist.
                        help='If the specified file does not exist, '
                        'falls back to environment variables: '
                        'First, INPUT_JSON or INPUT_JSON_URL, '
                        'and if neither of those exist, FILE_URLS.')
    parser.add_argument('--port', type=int, default=80)
    # During development, it's useful to be able to specify a high port.
    return parser


def error_page(e):
    error_str = ''.join(
        traceback.TracebackException.from_exception(e).format()
    )
    warn(error_str)

    html_doc = '''
                <html><head><title>Error</title></head><body>
                <p>An error has occurred: There may be a problem with the
                input provided. To report a bug, please copy this page and
                paste it in a <a href="{url}">bug report</a>. Thanks!</p>
                <pre>{stack}</pre>
                </body></html>'''.format(
        url='https://github.com/refinery-platform/'
            'heatmap-scatter-dash/issues/new',
        stack=html.escape(error_str))

    os.chdir(mkdtemp())
    open('index.html', 'w').write(html_doc)

    httpd = HTTPServer(('', 80), SimpleHTTPRequestHandler)
    httpd.serve_forever()


if __name__ == '__main__':
    try:
        args = RunnerArgs(arg_parser().parse_args())

        print('args from {}: {}'.format(__name__, args))
        assert args.files

        app_runner.main(args)
    except Exception as e:
        error_page(e)
