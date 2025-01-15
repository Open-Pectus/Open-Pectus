from argparse import ArgumentParser
from pylsp.python_lsp import start_ws_lang_server, PythonLSPServer


def get_args():
    parser = ArgumentParser("Start standalone Open Pevtus LSP server")
    parser.add_argument("-p", "--port", type=int, default=2087, help="Bind to this port")
    return parser.parse_args()


if __name__ == "__main__":
    print("Starting LSP server")

    # start lsp server process such that plugins can be debugged
    args = get_args()
    start_ws_lang_server(args.port, False, PythonLSPServer)
