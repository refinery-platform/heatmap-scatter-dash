#!/usr/bin/env python
import argparse
import json

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
        self.port = 80
        self.demo = False

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
    return parser


if __name__ == '__main__':
    args = RunnerArgs(arg_parser().parse_args())
    app_runner.main(args)
