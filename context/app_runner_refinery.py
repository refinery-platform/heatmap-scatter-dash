#!/usr/bin/env python
import argparse
import json
import os
from urllib.parse import urlparse

import requests

import app_runner


class RunnerArgs():
    """
    Initialized with an args object for app_runner_refinery.py,
    produces an args object for app_runner.py
    """

    def __init__(self, refinery_args):
        defaults = app_runner.arg_parser().parse_args(['--demo', '1', '1'])
        # We clobber the '--demo' setting just below.
        # This seemed more clear than reading the JSON first,
        # getting the files from it, and then passing them through parse_args,
        # but I could be wrong.
        for k, v in vars(defaults).items():
            setattr(self, k, v)
        self.demo = False
        self.port = refinery_args.port

        input = json.loads(refinery_args.input.read(None))
        parameters = {
            p['name']: p['value'] for p in input['parameters']
        }
        assert len(parameters) == 2

        self.cluster_rows = parameters['Cluster Rows']
        self.cluster_cols = parameters['Cluster Cols']
        assert type(self.cluster_rows) == bool
        assert type(self.cluster_cols) == bool

        self.api_prefix = input['api_prefix']
        assert type(self.api_prefix) == str

        data_directory = input['extra_directories'][0]
        try:
            self.files = self._download_files(
                input['file_relationships'][0],
                data_directory
            )
            self.diffs = self._download_files(
                input['file_relationships'][1],
                data_directory
            )
        except OSError as e:
            raise Exception('Does {} exist?'.format(data_directory)) from e

    def _download_files(self, urls, data_dir):
        """
        Given a list of urls and a target directory,
        download the files to the target, and return a list of filenames.
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
                name = url.split("/")[-1]
                path = '{}{}'.format(data_dir, name)
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        # filter out KEEP-ALIVE new chunks
                        if chunk:
                            f.write(chunk)
                files.append(open(path))
            finally:
                response.close()
        return files

    def __repr__(self):
        return '\n'.join(
            ['{}: {}'.format(k, v) for k, v in vars(self).items()]
        )


def arg_parser():
    parser = argparse.ArgumentParser(
        description='Webapp for visualizing differential expression')
    parser.add_argument('--input',
                        type=argparse.FileType('r'), required=True)
    parser.add_argument('--port',
                        type=int, default=80)
    # During development, it's useful to be able to specify a high port.
    return parser


if __name__ == '__main__':
    args = RunnerArgs(arg_parser().parse_args())

    print('args from {}: {}'.format(__name__, args))
    assert args.files

    app_runner.main(args)
