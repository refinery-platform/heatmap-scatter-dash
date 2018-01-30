import app_runner

if __name__ == "__main__":
    parser = app_runner.arg_parser()
    args = parser.parse_args(['--demo', '10', '10'])
    app_runner.main(args, parser)
