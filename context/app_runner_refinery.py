import argparse
import json

import app_runner


class RunnerArgs():
    """
    Given a args object appropriate for app_runner_refinery.py,
    produces an object appropriate for app_runner.py
    """
    def __init__(self, refinery_args):
        self.demo = False
        self.files = refinery_args.files
        self.port = refinery_args.port
        self.debug = False

        input = json.loads(refinery_args.input.read(None))
        parameters = {
            p['name']: p['value'] for p in input['parameters']
        }
        assert len(parameters) == 1
        assert parameters['Cluster'] in ['true', 'false']
        self.cluster = parameters['Cluster'] == 'true'


parser = argparse.ArgumentParser(
    description='Plotly Dash visualization for Refinery')
parser.add_argument('--input',
                    type=argparse.FileType('r'), required=True)
parser.add_argument('--files',
                    nargs='+', type=argparse.FileType('r'), required=True)
parser.add_argument('--port',
                    type=int, default=80)
args = RunnerArgs(parser.parse_args())

app_runner.main(args)
