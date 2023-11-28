import asyncio
import logging
from argparse import ArgumentParser

from openpectus import log_setup_colorlog
from openpectus.engine.demo_uod import create_demo_uod
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_reporter import EngineReporter
from protocol.engine_dispatcher import EngineDispatcher

log_setup_colorlog()

logger = logging.getLogger("openpectus.protocol.engine")
logger.setLevel(logging.INFO)
logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)
logging.getLogger("Engine").setLevel(logging.INFO)


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ahn", "--aggregator_hostname", required=False, default="127.0.0.1",
                        help="Aggregator websocket host name. Default is 127.0.0.1")
    parser.add_argument("-ap", "--aggregator_port", required=False, default="9800",
                        help="Aggregator websocket port number. Default is 9800")
    parser.add_argument("-uod", "--uod", required=False, default="DemoUod", help="The UOD to use")
    return parser.parse_args()


async def async_main(args):
    # TODO: read uod from file
    uod = create_demo_uod()
    engine = Engine(uod, tick_interval=1)
    dispatcher = EngineDispatcher(f"{args.aggregator_hostname}:{args.aggregator_port}", engine.uod.instrument)
    engine_reporter = EngineReporter(engine, dispatcher)
    message_handlers = EngineMessageHandlers(engine, dispatcher)
    await engine_reporter.run_loop_async()


def main():
    args = get_args()
    logger.info("Engine starting")
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
