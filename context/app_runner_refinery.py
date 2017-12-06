import argparse

parser = argparse.ArgumentParser(
    description='Plotly Dash visualization for Refinery')
parser.add_argument('--input', type=argparse.FileType('r'))
parser.add_argument('--files', nargs='+', type=argparse.FileType('r'))
args = parser.parse_args()
