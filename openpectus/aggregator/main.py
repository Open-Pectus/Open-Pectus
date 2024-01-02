import logging
from argparse import ArgumentParser

from openpectus import log_setup_colorlog
from openpectus.aggregator.aggregator_server import AggregatorServer

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


def get_args():
    parser = ArgumentParser("Start Aggregator server")
    parser.add_argument("-host", "--host", required=False, default=AggregatorServer.default_host,
                        help="Host address to bind frontend and web socket to")
    parser.add_argument("-p", "--port", required=False, type=int, default=AggregatorServer.default_port,
                        help="Host port to bind frontend and web socket to")
    parser.add_argument("-fdd", "--frontend_dist_dir", required=False, default=AggregatorServer.default_frontend_dist_dir,
                        help="Frontend distribution directory. Defaults to " + AggregatorServer.default_frontend_dist_dir)
    parser.add_argument("-dbpath", "--database_file_path", required=False, default=AggregatorServer.default_database_file_path,
                        help="SQLite database file path. Defaults to " + AggregatorServer.default_database_file_path)
    return parser.parse_args()


def main():
    args = get_args()
    title = "Pectus Aggregator"
    print(f"*** {title} ***")
    AggregatorServer(title, args.host, args.port, args.frontend_dist_dir, args.database_file_path).start()


if __name__ == "__main__":
    main()
