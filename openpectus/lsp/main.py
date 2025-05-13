import asyncio
import logging
import os
import threading
import time
from argparse import ArgumentParser, BooleanOptionalAction
from logging.handlers import RotatingFileHandler
import webbrowser

import alembic.command
import alembic.config
import httpx

import openpectus.aggregator.main
from openpectus.aggregator.aggregator_server import AggregatorServer
from openpectus.engine.configuration import demo_uod
from openpectus.engine.main import main_async
from openpectus.engine.main import get_arg_parser as engine_arg_parser

def aggregator_task(port: int):
    """ Adapted from main method in openpectus.aggregator.main """

    # Initialize database
    alembic_ini_file_path = os.path.join(os.path.dirname(openpectus.aggregator.main.__file__), "alembic.ini")
    local_aggregator_db_filepath = os.path.join(os.path.dirname(__file__), "lsp_db.sqlite3")
    alembic_config = alembic.config.Config(alembic_ini_file_path)
    alembic_config.set_main_option("sqlalchemy.url", f"sqlite:///{local_aggregator_db_filepath}")
    alembic.command.upgrade(alembic_config, "head")

    # Instantiate server
    server = AggregatorServer(
        "Open Pectus Aggregator for LSP development",
        "127.0.0.1",
        port,
        AggregatorServer.default_frontend_dist_dir,
        local_aggregator_db_filepath,
        "",
    )

    # Start aggregator server
    server.start()

def engine_task(port: int, uod_file_path: str, console_log: bool = False):
    """ Adapted from main method in openpectus.engine.main """

    # setup LSP loggers
    file_log_path = os.path.join(os.path.dirname(__file__), 'pylsp-openpectus.log')
    file_handler = RotatingFileHandler(file_log_path, maxBytes=2*1024*1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s',
                              datefmt='%Y-%m-%d %H:%M:%S'))
    # Set level
    logging.getLogger("openpectus.lsp.pylsp_plugin").setLevel(logging.DEBUG)
    logging.getLogger("openpectus.lsp.lsp_analysis").setLevel(logging.DEBUG)
    logging.getLogger("pylsp").setLevel(logging.WARNING)

    # Set logger handlers
    logging.root.handlers.clear()
    for logger in ["openpectus.lsp.pylsp_plugin", "openpectus.lsp.lsp_analysis", "lsp"]:
        logging.getLogger(logger).addHandler(file_handler)
        if console_log:
            logging.getLogger(logger).addHandler(logging.StreamHandler())

    # Set engine arguments
    args = engine_arg_parser().parse_args("")  # Don't parse from sys.argv
    args.aggregator_port = port  # Set proper aggregator port
    args.uod = uod_file_path  # Set UOD file path

    loop = asyncio.new_event_loop()

    # Run main_async without caring about graceful shutdown
    # The thread is daemon and the aggregator is going down
    # along with it anyways.
    loop.run_until_complete(main_async(args, loop))

def get_args():
    parser = ArgumentParser("Start Open Pectus aggregator with demo_uod for LSP development purposes.")
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=2087,
        help="Aggregator port. Default: 2087"
    )
    parser.add_argument(
        "-u",
        "--uod",
        type=str,
        default=demo_uod.__file__,
        help=f"Engine UOD. Default: {demo_uod.__file__}"
    )
    parser.add_argument(
        "-c",
        "--console_log",
        action=BooleanOptionalAction,
        default=False,
        help="Log to console as well as file"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()

    # Define thread objects
    aggregator_thread = threading.Thread(
        name="Aggregator",
        target=aggregator_task,
        args=(args.port,),
        daemon=True,
    )
    engine_thread = threading.Thread(
        name="Engine",
        target=engine_task,
        args=(args.port, args.uod, args.console_log),
        daemon=True,
    )

    # Start aggregator
    aggregator_thread.start()

    # Wait until aggregator is ready
    while True:
        try:
            httpx.get(f"http://127.0.0.1:{args.port}")
            break
        except httpx.HTTPError:
            time.sleep(0.1)

    # Aggregator is ready. Start engine and run forever
    engine_thread.start()
    try:
        key = input(f"Press enter to open aggregator website: http://127.0.0.1:{args.port}")
        if key == "":
            webbrowser.open(f"http://127.0.0.1:{args.port}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
