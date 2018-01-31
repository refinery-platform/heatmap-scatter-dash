import app_runner

# TODO: reference files in gitignored subdirectory
args = app_runner.arg_parser().parse_args(['--demo', '10', '10'])
application = app_runner.init(args, None)
