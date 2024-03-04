from __future__ import annotations
import logging
import time

from openpectus.engine.internal_commands import InternalEngineCommand
from openpectus.engine.models import EngineCommandEnum, MethodStatusEnum, SystemStateEnum
from openpectus.lang.exec.tags import SystemTagName
from openpectus.engine.engine import Engine


logger = logging.getLogger(__name__)


# Note:
# classes in this file are auto-registered as internal engine
# commands during engine initialization, by
# openpectus.engine.internal_commands.register_commands()


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
            e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)


class PauseEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.PAUSE)
        self.engine = engine

    def _run(self):
        e = self.engine
        e._runstate_paused = True
        e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Paused, e._tick_time)
        e._prev_state = e._apply_safe_state()


class UnpauseEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.UNPAUSE)
        self.engine = engine

    def _run(self):
        e = self.engine

        e._runstate_paused = False
        if e._runstate_holding:
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Holding, e._tick_time)
        else:
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)

        # pre-pause values are always applied on unpause, regardless of hold state.
        if e._prev_state:
            e._apply_state(e._prev_state)
        else:
            logger.error("Failed to apply state prior to safe state. Prior state was not available")

        # TODO Consider how a corrected error should be handled. It depends on the cause
        # - Run time value is broken: Maybe trying again will fix it
        # - Code is broken and the user fixes it: The interpreter should resume from the error node
        # which can be complex and requires the full editing feature. For now, we just take the error
        # flag down and hope for the best
        e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)

class HoldEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.HOLD)
        self.engine = engine

    def _run(self):
        e = self.engine
        e._runstate_holding = True
        if not e._runstate_paused:  # Pause takes precedence
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Holding, e._tick_time)


class UnholdEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.UNHOLD)
        self.engine = engine

    def _run(self):
        e = self.engine
        e._runstate_holding = False
        if not e._runstate_paused:  # Pause takes precedence
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

            for tag in e.tags:
                try:
                    tag.stop()
                except Exception:
                    logger.error(f"Error invoking stop on tag {tag.name}", exc_info=True)

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

            logger.debug("Restarting engine - uod commands have completed execution")
            e._runstate_started = False
            e._runstate_paused = False
            e._runstate_holding = False
            e._runstate_stopping = False
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, e._tick_time)

            for tag in e.tags:
                try:
                    tag.stop()
                except Exception:
                    logger.error(f"Error invoking stop on tag {tag.name}", exc_info=True)

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
