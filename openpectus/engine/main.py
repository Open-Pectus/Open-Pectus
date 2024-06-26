import asyncio
import logging
from argparse import ArgumentParser, BooleanOptionalAction
import importlib

from openpectus import log_setup_colorlog, sentry
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_reporter import EngineReporter
from openpectus.engine.hardware_recovery import ErrorRecoveryConfig, ErrorRecoveryDecorator
from openpectus.lang.exec.tags import SystemTagName, TagCollection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.protocol.engine_dispatcher import EngineDispatcher, EngineDispatcherBase
from openpectus.protocol.engine_dispatcher_error import EngineDispatcherErrorRecoveryDecorator

log_setup_colorlog()

logger = logging.getLogger("openpectus.engine.engine")
logger.setLevel(logging.INFO)
logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)
logging.getLogger("openpectus.protocol.engine_dispatcher").setLevel(logging.DEBUG)
logging.getLogger("openpectus.protocol.engine_dispatcher_error").setLevel(logging.DEBUG)
logging.getLogger("openpectus.engine.engine_reporter").setLevel(logging.DEBUG)


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ahn", "--aggregator_hostname", required=False, default="127.0.0.1",
                        help="Aggregator websocket host name. Default is 127.0.0.1")
    parser.add_argument("-ap", "--aggregator_port", required=False, default="9800",
                        help="Aggregator websocket port number. Default is 9800")
    parser.add_argument("-uod", "--uod", required=False, default="demo_uod", help="The UOD to use")
    parser.add_argument("-validate", "--validate", action=BooleanOptionalAction, help="Run Uod validation and exit")
    parser.add_argument("-sev", "--sentry_event_level", required=False,
                        default=sentry.EVENT_LEVEL_DEFAULT, choices=sentry.EVENT_LEVEL_NAMES,
                        help=f"Minimum log level to send as sentry events. Default is '{sentry.EVENT_LEVEL_DEFAULT}'")
    return parser.parse_args()


engine: Engine
dispatcher: EngineDispatcherBase
reporter: EngineReporter

def run_validations(uod: UnitOperationDefinitionBase) -> bool:
    try:
        logger.info("Verifying hardware configuration and connection")
        uod.validate_configuration()
        uod.hwl.validate_offline()
        uod.hwl.connect()
        uod.hwl.validate_online()
        logger.info("Hardware validation successful")
        return True
    except Exception:
        logger.error("An hardware related error occurred. Engine cannot start.")
        return False

async def main_async(args):
    global engine, dispatcher, reporter
    uod = create_uod(args.uod)
    engine = Engine(uod, tick_interval=0.1, enable_archiver=True)
    dispatcher = EngineDispatcher(
        f"{args.aggregator_hostname}:{args.aggregator_port}",
        engine.uod.instrument,
        engine.uod.location)

    if not run_validations(uod):
        exit(1)

    sentry.set_engine_uod(uod)

    # wrap hwl with error recovery decorator
    connection_status_tag = engine._system_tags[SystemTagName.CONNECTION_STATUS]
    uod.hwl = ErrorRecoveryDecorator(uod.hwl, ErrorRecoveryConfig(), connection_status_tag)

    # wrap dispatcher with error recovery decorator
    dispatcher = EngineDispatcherErrorRecoveryDecorator(dispatcher)

    reporter = EngineReporter(engine, dispatcher)
    _ = EngineMessageHandlers(engine, dispatcher)

    # TODO Possibly check dispatcher.check_aggregator_alive() and exit early

    # Whether we need this or not is ultimately as protocol decision
    # if aggregator only needs the config messages once, we get a simpler protocol
    # with fewer states.
    dispatcher.connected_callback = reporter.restart
    dispatcher.disconnected_callback = reporter.build_reconnected_message
    dispatcher.reconnected_callback = reporter.send_reconnected_message
    await dispatcher.connect_async()
    engine.run()

    while True:
        try:
            await reporter.send_data_messages()  # this is what drives the buffering of messages for recovering
            await asyncio.sleep(1)
        except Exception:
            logger.error("Unhandled exception in main loop. Trying to continue", exc_info=True)
            await asyncio.sleep(5)


async def close_async():
    global engine, dispatcher, reporter
    logger.debug("Stopping engine components")
    if engine is not None:
        engine.stop()
    if dispatcher is not None:
        await dispatcher.disconnect_async()
    logger.debug("Engine components stopped. Exiting")


def create_uod(uod_name: str) -> UnitOperationDefinitionBase:
    if uod_name is None or uod_name == "" or not isinstance(uod_name, str):
        raise ValueError("Uod is not specified")

    uod_module_package = "openpectus.engine.configuration." + uod_name

    try:
        uod_module = importlib.import_module(uod_module_package)
        logger.info(f"Imported uod '{uod_name}' from path '{uod_module.__file__}'")
    except Exception as ex:
        raise Exception("Failed to import uod module " + uod_module_package) from ex

    try:
        uod = uod_module.create()
        logger.info(f"Created uod: {uod}")
        return uod
    except Exception as ex:
        raise Exception("Failed to create uod instance") from ex


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
    sentry.init_engine(args.sentry_event_level)
    if args.validate:
        validate_and_exit(args.uod)

    logger.info("Engine starting")

    # Handling KeyboardInterrupt seems to fix the halt that sometimes otherwise occurs. But we still get the error:
    # "sys:1: RuntimeWarning: coroutine 'EngineDispatcher.disconnect_async' was never awaited"
    # https://stackoverflow.com/questions/54525836/where-do-i-catch-the-keyboardinterrupt-exception-in-this-async-setup#54528397
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_async(args))
        logger.info("Loop terminated - should only occur on stop")
    except KeyboardInterrupt:
        logger.info("User requested engine to stop")
        loop.run_until_complete(close_async())
    except Exception:
        logger.error("Unhandled exception in main. Stopping", exc_info=True)
        loop.run_until_complete(close_async())

    logger.info("Engine stopped")


if __name__ == "__main__":
    main()
