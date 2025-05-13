import logging
import os
from argparse import ArgumentParser

from alembic import command
from alembic.config import Config
from openpectus import log_setup_colorlog
from openpectus.aggregator.aggregator_server import AggregatorServer
from openpectus import sentry, __version__, build_number

# - add lsp thingys
# - start (manage) lsp server instance for each client

# Start env in docker
# ../docker compose up --build

log_setup_colorlog(root_loglevel=logging.INFO)
logger = logging.getLogger("openpectus.aggregator.aggregator")
logger.setLevel(logging.INFO)
logging.getLogger("openpectus.protocol.aggregator_dispatcher").setLevel(logging.INFO)

def get_arg_parser():
    parser = ArgumentParser("Start Aggregator server")
    parser.add_argument("-host", "--host", required=False, default=AggregatorServer.default_host,
                        help=f"Host address to bind frontend and WebSocket to. Default: {AggregatorServer.default_host}")
    parser.add_argument("-p", "--port", required=False, type=int, default=AggregatorServer.default_port,
                        help=f"Host port to bind frontend and WebSocket to. Default: {AggregatorServer.default_port}")
    parser.add_argument("-fdd", "--frontend_dist_dir", required=False, default=AggregatorServer.default_frontend_dist_dir,
                        help=f"Frontend distribution directory. Default: {AggregatorServer.default_frontend_dist_dir}")
    parser.add_argument("-sev", "--sentry_event_level", required=False,
                        default=sentry.EVENT_LEVEL_DEFAULT, choices=sentry.EVENT_LEVEL_NAMES,
                        help=f"Minimum log level to send as sentry events. Default: '{sentry.EVENT_LEVEL_DEFAULT}'")
    parser.add_argument("-db", "--database", required=False, default=AggregatorServer.default_db_path,
                        help=f"Path to Sqlite3 database. Default: ./{AggregatorServer.default_db_filename}")
    parser.add_argument("-secret", "--secret", required=False, default=AggregatorServer.default_secret,
                        help="Engines must know this secret to connect to the aggregator")
    return parser


def main():
    args = get_arg_parser().parse_args()
    title = "Open Pectus Aggregator"
    logger.info(f"Starting {title} v. {__version__}, build: {build_number}")
    logger.info(f"Serving frontend at http://{args.host}:{args.port}")
    if os.getenv("SENTRY_DSN"):
        logger.info(f"Sentry is active with DSN={os.getenv('SENTRY_DSN')}")
    else:
        logger.info("Sentry is not active.")
    if os.getenv("ENABLE_AZURE_AUTHENTICATION", default="").lower() == "true":
        logger.info("Authentication is active.")
    else:
        logger.info("Authentication is not active.")
    sentry.init_aggregator(args.sentry_event_level)
    alembic_ini_file_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
    alembic_config = Config(alembic_ini_file_path)
    alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{args.database}")
    command.upgrade(alembic_config, "head")

    server = AggregatorServer(title, args.host, args.port, args.frontend_dist_dir, args.database, args.secret)

    # seart aggregator server
    server.start()


if __name__ == "__main__":
    main()
