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

        input = json.loads(refinery_args.input.read(None))

        parameters = {
            p['name']: p['value'] for p in input['parameters']
        }
        assert len(parameters) == 1
        assert parameters['Cluster'] in ['true', 'false']
        self.cluster = parameters['Cluster'] == 'true'

        files = self._download_files(input['file_relationships'])

    def _download_files(urls, data_dir):
        """
        Download remote files specified by urls in the input.json file
        :param data_dir: <String> Path to directory to populate with data
        """
        with open("/data/input.json") as f:
            config_data = json.loads(f.read())

        for url in urls:
            try:
                # Streaming GET for potentially large files
                response = requests.get(url, stream=True)
            except requests.exceptions.RequestException as e:
                raise Exception(
                    "Error fetching {} : {}".format(url, e)
                )
            else:
                with open('{}{}'.format(data_dir, url.split("/")[-1]), 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        # filter out KEEP-ALIVE new chunks
                        if chunk:
                            f.write(chunk)
            finally:
                response.close()


parser = argparse.ArgumentParser(
    description='Plotly Dash visualization for Refinery')
parser.add_argument('--input',
                    type=argparse.FileType('r'), required=True)
parser.add_argument('--port',
                    type=int, default=80)
args = RunnerArgs(parser.parse_args())

app_runner.main(args)
