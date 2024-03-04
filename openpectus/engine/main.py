import asyncio
import logging
from argparse import ArgumentParser, BooleanOptionalAction

from openpectus import log_setup_colorlog
from openpectus.engine.demo_uod import create_demo_uod
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_reporter import EngineReporter
from openpectus.lang.exec.tags import TagCollection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.protocol.engine_dispatcher import EngineDispatcher

log_setup_colorlog()

logger = logging.getLogger("openpectus.engine.engine")
logger.setLevel(logging.INFO)
logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ahn", "--aggregator_hostname", required=False, default="127.0.0.1",
                        help="Aggregator websocket host name. Default is 127.0.0.1")
    parser.add_argument("-ap", "--aggregator_port", required=False, default="9800",
                        help="Aggregator websocket port number. Default is 9800")
    parser.add_argument("-uod", "--uod", required=False, default="DemoUod", help="The UOD to use")
    parser.add_argument("-validate", "--validate", action=BooleanOptionalAction, help="Run Uod validation and exit")
    return parser.parse_args()


async def async_main(args):
    uod = create_uod(args.uod)
    engine = Engine(uod, tick_interval=1)
    dispatcher = EngineDispatcher(
        f"{args.aggregator_hostname}:{args.aggregator_port}",
        engine.uod.instrument,
        engine.uod.location)
    await dispatcher.connect_websocket_async()
    engine_reporter = EngineReporter(engine, dispatcher)
    args.engine_reporter = engine_reporter
    _ = EngineMessageHandlers(engine, dispatcher)
    await engine_reporter.run_loop_async()


async def close_async(engine_reporter: EngineReporter):
    if (engine_reporter):
        await engine_reporter.stop_async()


def create_uod(uod_name: str) -> UnitOperationDefinitionBase:
    if uod_name == "DemoUod":
        return create_demo_uod()
    else:
        raise NotImplementedError("TODO create uod from name")


def validate_and_exit(uod_name: str):
    logger.info("Engine started in validation mode")

    try:
        uod = create_uod(uod_name)
        logger.info(f"Uod '{uod_name}' created successfully")
    except Exception:
        logger.error(f"Validation failed. Failed to create uod '{uod_name}'", exc_info=True)
        exit(1)

    uod.system_tags = TagCollection.create_system_tags()

    logger.info("Validating uod configuration")
    uod.validate_configuration()

    try:
        logger.info("Running offline hardware validation")
        uod.hwl.validate_offline()
        logger.info("Offline validation successful")
    except Exception:
        logger.error("Offline validation failed", exc_info=True)
        exit(1)

    logger.info("Running online hardware validation")
    try:
        logger.info("Connecting to hardware")
        uod.hwl.connect()
        logger.info("Hardware connected")
    except Exception:
        logger.info("Hardware connection failed", exc_info=True)
        exit(1)

    try:
        uod.hwl.validate_online()
        logger.info("Online validation successful")
    except Exception:
        logger.error("Online validation failed", exc_info=True)

    logger.info("Validation complete. Exiting.")
    exit(0)


def main():
    args = get_args()

    if args.validate:
        validate_and_exit(args.uod)

    logger.info("Engine starting")

    # Handling KeyboardInterrupt seems to fix the halt that sometimes otherwise occurs. But we still get the error:
    # "sys:1: RuntimeWarning: coroutine 'EngineDispatcher.disconnect_async' was never awaited"
    # https://stackoverflow.com/questions/54525836/where-do-i-catch-the-keyboardinterrupt-exception-in-this-async-setup#54528397
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(async_main(args))
    except KeyboardInterrupt:
        loop.run_until_complete(close_async(args.engine_reporter))
    finally:
        print('Engine stopped')


if __name__ == "__main__":
    main()
