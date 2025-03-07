from argparse import ArgumentParser, BooleanOptionalAction
import logging
import logging.config
import os
import pathlib
from logging.handlers import RotatingFileHandler
from pylsp.python_lsp import start_ws_lang_server, PythonLSPServer

# command line to start pyslp server from Open-Pectus directory
# pylsp --ws -vv --log-file openpectus/lsp/pylsp-openpectus.log

# setup LSP loggers
file_log_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'pylsp-openpectus.log')
file_handler = RotatingFileHandler(file_log_path, maxBytes=2*1024*1024, backupCount=5)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s %(name)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logging.basicConfig(format='%(name)s :: %(levelname)-8s :: %(message)s', level=logging.WARNING, handlers=[file_handler])

logging.getLogger("openpectus.lsp.pylsp_plugin").setLevel(logging.DEBUG)
logging.getLogger("openpectus.lsp.lsp_analysis").setLevel(logging.DEBUG)
logging.getLogger("pylsp").setLevel(logging.WARNING)


def get_args():
    parser = ArgumentParser("Start standalone Open Pectus LSP server")
    parser.add_argument("--port", type=int, default=2087, help="Bind to this port")
    parser.add_argument("--aggregator_url", type=str, default="http://localhost:9800",
                        help="Url to Aggregator service, e.g. 'https://openpectus.org:9800'")
    parser.add_argument("--console_log", action=BooleanOptionalAction, default=False, help="Log to console as well as file")
    parser.add_argument("--watch_parent", action=BooleanOptionalAction, default=False,
                        help="Watch parent process and terminate with it")
    return parser.parse_args()


if __name__ == "__main__":
    #global aggregator_url
    print("Starting LSP server")
    # start lsp server process such that plugins can be debugged
    args = get_args()
    import openpectus.lsp.config as config
    config.aggregator_url = args.aggregator_url
    if args.console_log:
        logging.root.addHandler(logging.StreamHandler())

    start_ws_lang_server(args.port, args.watch_parent, PythonLSPServer)
