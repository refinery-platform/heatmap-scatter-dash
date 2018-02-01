#!/usr/bin/env python
import argparse
import json

import requests
from app.utils.resource_loader import relative_path

def arg_parser():
    parser = argparse.ArgumentParser(
        description='Webapp for visualizing differential expression')
    parser.add_argument(
        '--files', nargs='+', metavar='CSV', required=True,
        type=argparse.FileType('r'),
        help='Read CSV or TSV files. Identifiers should be in the first '
             'column and multiple files will be joined on identifier. '
             'Compressed files are also handled, '
             'if correct extension is given. (ie ".csv.gz")')

    parser.add_argument(
        '--diffs', nargs='+', metavar='CSV',
        type=argparse.FileType('r'), default=[],
        help='Read CSV or TSV files containing differential expression data.')
    # During development, it's useful to be able to specify a high port.
    return parser

def input():
    return {
      "api_prefix": "/",
      "api_prefix NOTE": "Should actually be something like: /visualizations/container-name/",
      "file_relationships": [
        ["file:///data/counts.csv"],
        [
          "file:///data/stats-with-genes-in-col-1.csv",
          "file:///data/stats-with-genes-in-col-2.tsv"
        ]
      ],
      "extra_directories": [
        "/data/"
      ],
      "node_info": {
        "some-refinery-uuid-1": {
          "file_url": "file:///data/counts.csv",
          "node_solr_info": {
            "A lot of data here...": "but I feel uncomfortable binding myself to these ugly internal names.",
            "It needs a clean API": "True!"
          }
        },
        "some-refinery-uuid-2": {
          "file_url": "file:///data/stats-with-genes-in-col-1.csv",
          "node_solr_info": {}
        },
        "some-refinery-uuid-3": {
          "file_url": "file:///data/stats-with-genes-in-col-2.tsv",
          "node_solr_info": {}
        }
      },
      "parameters": [
        {
          "name": "Cluster Rows",
          "description": "Should rows of heatmap be clustered?",
          "value_type": "BOOLEAN",
          "default_value": False,
          "value": True
        },
        {
          "name": "Cluster Cols",
          "description": "Should columns of heatmap be clustered?",
          "value_type": "BOOLEAN",
          "default_value": False,
          "value": True
        }
      ]
    }

if __name__ == '__main__':
    args = arg_parser().parse_args()
    input_json = json.dumps(input())
    with open(relative_path(__file__,'data/input.json'), 'w') as f:
        f.write(input_json)