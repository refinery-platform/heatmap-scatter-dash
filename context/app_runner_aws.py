#!/usr/bin/env python
import argparse
import json

from os import mkdir, symlink
from os.path import basename, join, abspath
from shutil import rmtree

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

def input(file_urls=[], diff_urls=[]):
    return {
      "api_prefix": "/",
      "api_prefix NOTE": "Should be something like: /visualizations/container-name/",
      "api_prefix NOTE2": "... except not sure we have the container name from EB before launch?",
      "file_relationships": [
        file_urls,
        diff_urls
      ],
      "extra_directories": [
        "/data/"
      ],
      "node_info": {},
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

def links_and_urls(files, data_dir):
    # Given a list of files, creates links and returns a list of urls.
    dir_base = basename(data_dir)
    file_urls = []
    for file in files:
        dest_base = basename(file.name)
        dest = join(data_dir, dest_base)
        symlink(abspath(file.name), dest)
        file_urls.append("file:///{}/{}".format(dir_base, dest_base))
    return file_urls

if __name__ == '__main__':
    args = arg_parser().parse_args()

    data_dir = relative_path(__file__, 'data')
    rmtree(data_dir)
    mkdir(data_dir)

    file_urls = links_and_urls(args.files, data_dir)
    diff_urls = links_and_urls(args.diffs, data_dir)

    input_json = json.dumps(
        input(
            file_urls=file_urls,
            diff_urls=diff_urls,
        ),
        sort_keys=True, indent=4,
    )
    with open(join(data_dir, 'input.json'), 'w') as f:
        f.write(input_json)


    # TODO: start EB