import asyncio
import logging
from argparse import ArgumentParser
from typing import Any, List

from openpectus import log_setup_colorlog
from openpectus.engine.engine import Engine
from openpectus.engine.engine_reporter import EngineReporter
from openpectus.engine.hardware import RegisterDirection
from openpectus.engine.message_handlers import MessageHandlers
from openpectus.lang.exec import tags, readings as R
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodBuilder, UodCommand
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


def create_demo_uod() -> UnitOperationDefinitionBase:
    def reset(cmd: UodCommand, args: List[Any]) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset")
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A")
            cmd.set_complete()

    return (
        UodBuilder()
        .with_instrument("DemoUod")
        .with_no_hardware()
        .with_hardware_register("FT01", RegisterDirection.Both, path='Objects;2:System;2:FT01')
        .with_hardware_register("Reset", RegisterDirection.Both, path='Objects;2:System;2:RESET',
                                from_tag=lambda x: 1 if x == 'Reset' else 0,
                                to_tag=lambda x: "Reset" if x == 1 else "N/A")
        .with_new_system_tags()
        .with_tag(tags.Reading("FT01", "L/h"))
        .with_tag(tags.Select("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_process_value(R.Reading(label="Run Time"))
        .with_process_value(R.Reading(label="FT01"))
        .with_process_value(R.Reading(label="Reset"))
        .with_process_value(R.Reading(label="System State"))
        .build()
    )


async def async_main(args):
    # TODO: read uod from file
    uod = create_demo_uod()
    engine = Engine(uod, tick_interval=1)
    dispatcher = EngineDispatcher(f"{args.aggregator_hostname}:{args.aggregator_port}")
    engine_reporter = EngineReporter(engine, dispatcher)
    message_handlers = MessageHandlers(engine, dispatcher)
    await engine_reporter.run_loop_async()


def main():
    args = get_args()
    logger.info("Engine starting")
    asyncio.run(async_main(args))


if __name__ == "__main__":
    main()
