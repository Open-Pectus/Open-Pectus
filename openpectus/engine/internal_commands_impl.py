from __future__ import annotations
import logging
import time

from openpectus.engine.internal_commands import InternalEngineCommand
from openpectus.engine.models import EngineCommandEnum, SystemStateEnum
from openpectus.lang.exec.tags import SystemTagName
from openpectus.engine.engine import Engine

logger = logging.getLogger(__name__)

class StartEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.START)
        self.engine = engine

    def _run(self):
        e = self.engine
        if e._runstate_started:
            logger.warning("Cannot start when already running")
            self.fail()
        else:
            e._runstate_started = True
            e._runstate_started_time = time.time()
            e._runstate_paused = False
            e._runstate_holding = False
            e._set_run_id("new")
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)


class StopEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.STOP)
        self.engine = engine

    def _run(self):
        e = self.engine
        sys_state = e._system_tags[SystemTagName.SYSTEM_STATE]
        if sys_state.get_value() == SystemStateEnum.Stopped:
            logger.warning("Cannot stop when system state is already stopped")
            self.fail()
        elif sys_state.get_value() == SystemStateEnum.Restarting:
            logger.warning("Cannot stop when system state is restarting")
            self.fail()
        else:
            e._runstate_stopping = True
            e._cancel_uod_commands()
            timeout_at_tick = e._tick_number + 10
            while e.uod.has_any_command_instances():
                if e._tick_number > timeout_at_tick:
                    logger.warning("Time out waiting for uod commands to cancel")
                    break
                yield

            logger.debug("All uod commands have completed execution. Stop will now complete.")
            e._runstate_started = False
            e._runstate_paused = False
            e._runstate_holding = False
            e._runstate_stopping = False
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, e._tick_time)
            e._set_run_id("empty")
            e._stop_interpreter()


class RestartEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.RESTART)
        self.engine = engine

    def _run(self):
        e = self.engine
        sys_state = e._system_tags[SystemTagName.SYSTEM_STATE]
        if sys_state.get_value() == SystemStateEnum.Stopped:
            logger.warning("Cannot restart when system state is Stopped")
            self.fail()
        elif sys_state.get_value() == SystemStateEnum.Restarting:
            logger.warning("Cannot restart when system state is Restarting")
            self.fail()
        else:
            logger.info("Restarting engine")
            sys_state.set_value(SystemStateEnum.Restarting, e._tick_time)
            e._runstate_stopping = True
            e._cancel_uod_commands()

            yield  # make sure this state always lasts at least one full tick

            while e.uod.has_any_command_instances():
                yield

            logger.debug("All uod commands have completed execution. Stop will now complete.")
            e._runstate_started = False
            e._runstate_paused = False
            e._runstate_holding = False
            e._runstate_stopping = False
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, e._tick_time)
            e._set_run_id("empty")
            e._stop_interpreter()
            logger.info("Restarting engine - engine stopped")

            yield

            logger.info("Restarting engine - starting engine")
            # potentially a lot more engine state to reset
            e._runstate_started = True
            e._runstate_started_time = time.time()
            e._tick_number = 0
            e._runstate_paused = False
            e._runstate_holding = False
            e._set_run_id("new")
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)
            logger.info("Restarting engine complete")
