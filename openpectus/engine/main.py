import asyncio
import logging
from argparse import ArgumentParser, BooleanOptionalAction
import importlib
from logging.handlers import RotatingFileHandler
from os import path
import pathlib
from typing import Literal


from openpectus import log_setup_colorlog, sentry, __version__, build_number
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_message_builder import EngineMessageBuilder
from openpectus.engine.hardware import NullHardware
from openpectus.engine.hardware_recovery import ErrorRecoveryConfig, ErrorRecoveryDecorator
from openpectus.lang.exec.tags import SystemTagName, TagCollection
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.protocol.engine_dispatcher import EngineDispatcher
from openpectus.engine.engine_runner import EngineRunner

from openpectus.test.engine.utility_methods import EngineTestRunner

log_setup_colorlog()

StateKind = Literal["Started", "Connected", "Disconnected", "Reconnecting", "Reconnected"]

file_log_path = path.join(pathlib.Path(__file__).parent.resolve(), 'openpectus-engine.log')
file_handler = RotatingFileHandler(file_log_path, maxBytes=2*1024*1024, backupCount=5)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
logging.root.addHandler(file_handler)

logger = logging.getLogger("openpectus.engine.engine")
logger.setLevel(logging.INFO)

logging.getLogger("openpectus.lang.exec.pinterpreter").setLevel(logging.INFO)
logging.getLogger("openpectus.protocol.engine_dispatcher").setLevel(logging.INFO)
logging.getLogger("openpectus.engine.engine_runner").setLevel(logging.INFO)
logging.getLogger("openpectus.engine.internal_commands_impl").setLevel(logging.INFO)
logging.getLogger("asyncua.client").setLevel(logging.WARNING)


default_host = "127.0.0.1"
default_port = "9800"
default_port_secure = "443"


def get_args():
    parser = ArgumentParser("Start Pectus Engine")
    parser.add_argument("-ahn", "--aggregator_hostname", required=False, default=default_host,
                        help="Aggregator websocket host name. Default is 127.0.0.1")
    parser.add_argument("-ap", "--aggregator_port", required=False, default=None,
                        help=f"Aggregator websocket port number. Default is {default_port} or {default_port_secure} " +
                        "if using --secure")
    parser.add_argument("-s", "--secure", action=BooleanOptionalAction,
                        help="Access aggregator using https/wss rather than http/ws")
    parser.add_argument("-uod", "--uod", required=False, default="demo_uod", help="The UOD to use")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-validate", "--validate", action=BooleanOptionalAction,
                       help="Run Uod validation and exit. Cannot be used with -rd")
    group.add_argument("-rd", "--show_register_details", action=BooleanOptionalAction,
                       help="Show register details for UOD authoring and exit. Cannot be used with -validate")
    parser.add_argument("-sev", "--sentry_event_level", required=False,
                        default=sentry.EVENT_LEVEL_DEFAULT, choices=sentry.EVENT_LEVEL_NAMES,
                        help=f"Minimum log level to send as sentry events. Default is '{sentry.EVENT_LEVEL_DEFAULT}'")
    return parser.parse_args()


engine: Engine | None = None
runner: EngineRunner | None = None


def run_validations(uod: UnitOperationDefinitionBase) -> bool:
    try:
        logger.info("Verifying hardware configuration and connection")
        uod.validate_configuration()
        uod.hwl.validate_offline()
        uod.hwl.connect()
        uod.hwl.validate_online()
        logger.info("Hardware validation successful")

        logger.info("Building uod commands")
        uod.build_commands()
        return True
    except Exception:
        logger.error("An hardware related error occurred. Engine cannot start.")
        return False

async def main_async(args):
    global engine, runner
    try:
        uod = create_uod(args.uod)
    except Exception as ex:
        logger.error(f"Failed to create uod: {ex}")
        return

    engine = Engine(uod, enable_archiver=True)

    # if --aggregator_port is specified, use it, else select a default port based on --secure
    if args.aggregator_port is not None:
        port = args.aggregator_port
    else:
        port = default_port_secure if args.secure else default_port

    dispatcher = EngineDispatcher(f"{args.aggregator_hostname}:{port}", args.secure, uod.options)

    if not run_validations(uod):
        exit(1)

    sentry.set_engine_uod(uod)

    # wrap hwl with error recovery decorator
    connection_status_tag = engine._system_tags[SystemTagName.CONNECTION_STATUS]
    uod.hwl = ErrorRecoveryDecorator(uod.hwl, ErrorRecoveryConfig(), connection_status_tag)

    message_builder = EngineMessageBuilder(engine)
    # create runner that orchestrates the error recovery mechanism
    runner = EngineRunner(dispatcher, message_builder)
    _ = EngineMessageHandlers(engine, dispatcher)

    # TODO Possibly check dispatcher.check_aggregator_alive() and exit early


    async def on_steady_state():
        logger.info("Starting engine on first steady-state")
        assert engine is not None, "Engine was unexpectedly None on first stady_state"
        engine.run()

    runner.first_steady_state_callback = on_steady_state
    await runner.run()



async def close_async():
    global engine, runner
    logger.debug("Stopping engine components")
    if engine is not None:
        engine.stop()
    if runner is not None:
        await runner.shutdown()
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

    run_example_commands(uod)

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

def run_example_commands(uod: UnitOperationDefinitionBase):
    uod.build_commands()
    logger.info("Validating UOD command examples")
    uod.hwl = NullHardware()

    failed_cmds: list[str] = []
    for desc in uod.command_descriptions.values():
        logger.info(f"Executing example commands for uod command '{desc.name}'")
        pcode = desc.get_docstring_pcode()
        if pcode.strip() == "":
            logger.warning(f"Command '{desc.name} has no pcode example")
            continue
        try:
            runner = EngineTestRunner(uod_factory=lambda: uod, pcode=pcode)
            with runner.run() as instance:
                instance.start()
                # wait up to 1 minute, that oughta be enought for everybody
                instance.run_until_event("method_end", max_ticks=10*60)
                logger.debug(instance.get_runtime_table())
                logger.debug(f"Command '{pcode}' executed successfully")
        except Exception as ex:
            logger.error(f"Command '{pcode}' failed: {str(ex)}")
            failed_cmds.append(desc.name)

        examples = desc.generate_pcode_examples()
        for example in examples:
            try:
                runner = EngineTestRunner(uod_factory=lambda: uod, pcode=example)
                with runner.run() as instance:
                    instance.start()
                    instance.run_until_event("method_end", max_ticks=10*60)
                    logger.debug(instance.get_runtime_table())
                    logger.debug(f"Command '{desc.name}' executed successfully")
            except Exception as ex:
                logger.error(f"Command '{example}' failed: {str(ex)}")
                failed_cmds.append(example)

    if len(failed_cmds) > 0:
        logger.error(f"Example commands failed: {','.join(failed_cmds)}")
    else:
        logger.info("All example commands executed succesfully")

def show_register_details_and_exit(uod_name: str):
    logger.info("Engine started in register details mode")

    try:
        uod = create_uod(uod_name)
        logger.info(f"Uod '{uod_name}' created successfully")
    except Exception:
        logger.error(f"Validation failed. Failed to create uod '{uod_name}'", exc_info=True)
        exit(1)

    uod.system_tags = TagCollection.create_system_tags()

    try:
        logger.info("Connecting to hardware")
        uod.hwl.connect()
        logger.info("Hardware connected")
    except Exception:
        logger.info("Hardware connection failed", exc_info=True)
        exit(1)

    try:
        uod.hwl.show_online_register_details()
    except Exception:
        logger.error("Error showing register details")
        exit(1)

    exit(0)


def main():
    print(f"OpenPectus Engine v. {__version__}, build: {build_number}")
    args = get_args()
    sentry.init_engine(args.sentry_event_level)
    if args.validate:
        validate_and_exit(args.uod)
    elif args.show_register_details:
        show_register_details_and_exit(args.uod)

    logger.info("Engine starting")

    # Handling KeyboardInterrupt seems to fix the halt that sometimes otherwise occurs. But we still get the error:
    # "sys:1: RuntimeWarning: coroutine 'EngineDispatcher.disconnect_async' was never awaited"
    # https://stackoverflow.com/questions/54525836/where-do-i-catch-the-keyboardinterrupt-exception-in-this-async-setup#54528397
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main_async(args))
        logger.info("Main loop completed")
    except KeyboardInterrupt:
        logger.info("User requested engine to stop")
        loop.run_until_complete(close_async())
    except Exception:
        logger.error("Unhandled exception in main. Stopping.", exc_info=True)
        loop.run_until_complete(close_async())

    logger.info("Engine stopped")


if __name__ == "__main__":
    main()
