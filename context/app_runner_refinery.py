import argparse
import json

import requests

import app_runner


class RunnerArgs():
    """
    Given a args object appropriate for app_runner_refinery.py,
    produces an object appropriate for app_runner.py
    """

    def __init__(self, refinery_args):
        self.demo = False
        self.port = refinery_args.port
        self.debug = False
        self.heatmap = 'svg'  # TODO: Make a canvas that isn't fuzzy
        self.skip_zero = True
        self.colors = 'Greys'
        # TODO: Colors is not going to be configurable in Refinery,
        # so pick the right value and set it here.

        input = json.loads(refinery_args.input.read(None))

        parameters = {
            p['name']: p['value'] for p in input['parameters']
        }
        assert len(parameters) == 2
        assert parameters['Cluster Rows'] in [True, False]
        assert parameters['Cluster Cols'] in [True, False]
        self.cluster_rows = parameters['Cluster Rows']
        self.cluster_cols = parameters['Cluster Cols']

        self.files = self._download_files(
            input['file_relationships'],
            input['extra_directories'][0]
        )

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


parser = argparse.ArgumentParser(
    description='Plotly Dash visualization for Refinery')
parser.add_argument('--input',
                    type=argparse.FileType('r'), required=True)
parser.add_argument('--port',
                    type=int, default=80)
args = RunnerArgs(parser.parse_args())

app_runner.main(args)
