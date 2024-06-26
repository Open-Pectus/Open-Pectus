import logging
import os
from argparse import ArgumentParser

from alembic import command
from alembic.config import Config
from openpectus import log_setup_colorlog
from openpectus.aggregator.aggregator_server import AggregatorServer
from openpectus import sentry

# - add lsp thingys
# - start (manage) lsp server instance for each client
# - aggregator-engine protocol


# Start env in docker
# ../docker compose up --build

# start local
# python -m uvicorn main:app --reload --port 8300

# check generation openapi.json() from build action, see https://github.com/tiangolo/fastapi/issues/2877
# possibly https://pypi.org/project/fastapi-openapi-generator/

# hints for
# https://stackoverflow.com/questions/67849806/flask-how-to-automate-openapi-v3-documentation

# Look into this https://stackoverflow.com/questions/74137116/how-to-hide-a-pydantic-discriminator-field-from-fastapi-docs
# Final / Literal ...


log_setup_colorlog(root_loglevel=logging.INFO)
logger = logging.getLogger("openpectus.aggregator.aggregator")
logger.setLevel(logging.INFO)
logging.getLogger("openpectus.protocol.aggregator_dispatcher").setLevel(logging.DEBUG)

def get_args():
    parser = ArgumentParser("Start Aggregator server")
    parser.add_argument("-host", "--host", required=False, default=AggregatorServer.default_host,
                        help="Host address to bind frontend and web socket to")
    parser.add_argument("-p", "--port", required=False, type=int, default=AggregatorServer.default_port,
                        help="Host port to bind frontend and web socket to")
    parser.add_argument("-fdd", "--frontend_dist_dir", required=False, default=AggregatorServer.default_frontend_dist_dir,
                        help="Frontend distribution directory. Defaults to " + AggregatorServer.default_frontend_dist_dir)
    parser.add_argument("-sev", "--sentry_event_level", required=False,
                        default=sentry.EVENT_LEVEL_DEFAULT, choices=sentry.EVENT_LEVEL_NAMES,
                        help=f"Minimum log level to send as sentry events. Default is '{sentry.EVENT_LEVEL_DEFAULT}'")
    return parser.parse_args()


def main():
    args = get_args()
    title = "Pectus Aggregator"
    print(f"*** {title} ***")
    sentry.init_aggregator(args.sentry_event_level)
    alembic_ini_file_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
    command.upgrade(Config(alembic_ini_file_path), 'head')
    AggregatorServer(title, args.host, args.port, args.frontend_dist_dir).start()


if __name__ == "__main__":
    main()
