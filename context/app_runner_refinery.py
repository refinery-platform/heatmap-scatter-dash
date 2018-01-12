#!/usr/bin/env python
import argparse
import json

import requests

import app_runner


class DefaultArgs():

    def __init__(self):
        self.demo = False
        self.debug = False
        self.heatmap = 'svg'  # TODO: Make a canvas that isn't fuzzy
        self.skip_zero = True
        self.colors = 'Greys'
        self.most_variable_rows = 500
        self.reverse_colors = True
        self.html_error = True


class RunnerArgs(DefaultArgs):
    """
    Given an args object appropriate for app_runner_refinery.py,
    produces an object appropriate for app_runner.py
    """

    def __init__(self, refinery_args):
        super().__init__()
        self.port = refinery_args.port

        input = json.loads(refinery_args.input.read(None))
        parameters = {
            p['name']: p['value'] for p in input['parameters']
        }
        assert len(parameters) == 2

        assert type(parameters['Cluster Rows']) == bool
        assert type(parameters['Cluster Cols']) == bool
        self.cluster_rows = parameters['Cluster Rows']
        self.cluster_cols = parameters['Cluster Cols']

        assert type(input['api_prefix']) == str
        self.api_prefix = input['api_prefix']

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
                files.append(path)  # TODO: More unique?
                with open(path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        # filter out KEEP-ALIVE new chunks
                        if chunk:
                            f.write(chunk)
            finally:
                response.close()
        return files


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Webapp for visualizing differential expression')
    parser.add_argument('--input',
                        type=argparse.FileType('r'), required=True)
    parser.add_argument('--port',
                        type=int, default=80)
    args = RunnerArgs(parser.parse_args())

    app_runner.main(args)
