import argparse
from flaskphiid import create_app

app = create_app()

cmd_arg_parser = argparse.ArgumentParser("")
cmd_arg_parser.add_argument('-e',
                            default='0.0.0.0',
                            dest="endpoint",
                            help="Set endpoint. Default is 0.0.0.0 ")
cmd_arg_parser.add_argument('-p',
                            default='5000',
                            dest="port",
                            help="Set port. Default is 5000 ")
cmd_args = cmd_arg_parser.parse_args()

app.run(host=cmd_args.endpoint, port=cmd_args.port)
