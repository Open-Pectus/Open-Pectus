from __future__ import annotations
import logging
import time
from typing import Any

from openpectus.engine.internal_commands import InternalEngineCommand
from openpectus.engine.models import EngineCommandEnum, MethodStatusEnum, SystemStateEnum
from openpectus.lang.exec.tags import SystemTagName
from openpectus.engine.engine import Engine


logger = logging.getLogger(__name__)


# Note:
# classes in this file are auto-registered as internal engine commands during engine initialization, by
# openpectus.engine.internal_commands.register_commands()

def get_duration_end(tick_time: float, time: float, unit: str) -> float:
    if unit not in ['s', 'min', 'h']:
        raise ValueError(f"Wait argument unit must be a time unit, not '{unit}'")

    seconds = time
    if unit == 'min':
        seconds = 60 * time
    elif unit == 'h':
        seconds = 60 * 60 * time
    return tick_time + seconds


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
            e._system_tags[SystemTagName.RUN_TIME].set_value(0.0, e._tick_time)
            e._system_tags[SystemTagName.PROCESS_TIME].set_value(0.0, e._tick_time)
            e._system_tags[SystemTagName.RUN_COUNTER].set_value(0, e._tick_time)

            e._system_tags[SystemTagName.BLOCK_TIME].set_value(0.0, e._tick_time)
            e.block_times.clear()  # kinda hackish, tag should be self-contained

            e.tag_context.emit_on_start()


class PauseEngineCommand(InternalEngineCommand):
    """ Pause execution of commands and time. Put output tag into safe state.

    See also Hold and Wait.
    """
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.PAUSE)
        self.engine = engine
        self.duration_end_time : float | None = None

    def init_args(self, kvargs: dict[str, Any]):
        if "time" in kvargs.keys() and "unit" in kvargs.keys():
            time = float(kvargs.get("time", None))
            if time is None:
                raise ValueError("Invalid Pause arguments. Time is not valid")
            unit = kvargs.get("unit", None)
            if unit is None:
                raise ValueError("Invalid Pause arguments. Unit is not valid")
            self.duration_end_time = get_duration_end(self.engine._tick_time, time, unit)
        elif "time" in kvargs.keys() or "unit" in kvargs.keys():
            raise ValueError("Invalid Pause arguments. Specify either no duration arguments or both time and unit")

    def _run(self):
        e = self.engine
        e._runstate_paused = True
        e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Paused, e._tick_time)
        e._prev_state = e._apply_safe_state()

        if self.duration_end_time is not None:
            logger.debug("Pause duration set. Waiting to unpause.")
            while self.engine._tick_time < self.duration_end_time:
                yield
            logger.debug("Resuming using Unpause")
            UnpauseEngineCommand(self.engine)._run()


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
        if e._prev_state is not None:
            e._apply_state(e._prev_state)
            e._prev_state = None
        else:
            logger.error("Failed to apply state prior to safe state. Prior state was not available")

        # TODO Consider how a corrected error should be handled. It depends on the cause
        # - Run time value is broken: Maybe trying again will fix it
        # - Code is broken and the user fixes it: The interpreter should resume from the error node
        # which can be complex and requires the full editing feature. For now, we just take the error
        # flag down and hope for the best
        e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)


class HoldEngineCommand(InternalEngineCommand):
    """ Hold execution of commands and time, keeping ouput tags in their current state.

    See also Pause and Wait.
    """
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.HOLD)
        self.engine = engine
        self.duration_end_time : float | None = None

    def init_args(self, kvargs: dict[str, Any]):
        if "time" in kvargs.keys() and "unit" in kvargs.keys():
            time = float(kvargs.get("time", None))
            if time is None:
                raise ValueError("Invalid Hold arguments. Time is not valid")
            unit = kvargs.get("unit", None)
            if unit is None:
                raise ValueError("Invalid Hold arguments. Unit is not valid")
            self.duration_end_time = get_duration_end(self.engine._tick_time, time, unit)
        elif "time" in kvargs.keys() or "unit" in kvargs.keys():
            raise ValueError("Invalid Hold arguments. Specify either no duration arguments or both time and unit")

    def _run(self):
        e = self.engine
        e._runstate_holding = True
        if not e._runstate_paused:  # Pause takes precedence
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Holding, e._tick_time)

        if self.duration_end_time is not None:
            logger.debug("Hold duration set. Waiting to unhold.")
            while self.engine._tick_time < self.duration_end_time:
                yield
            logger.debug("Resuming using Unhold")
            UnholdEngineCommand(self.engine)._run()


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
            e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)

            e.tag_context.emit_on_stop()

            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, e._tick_time)
            e._set_run_id("empty")
            e._stop_interpreter()


class WaitEngineCommand(InternalEngineCommand):
    """ Pause execution of commands for the specified duration, keeping time running and output tags in their current state.

    See also Pause and Hold.
    """
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.WAIT)
        self.engine = engine

    def init_args(self, kvargs: dict[str, Any]):
        if "time" in kvargs.keys() and "unit" in kvargs.keys():
            time = float(kvargs.get("time", None))
            if time is None:
                raise ValueError("Invalid Wait arguments. Time is not valid")
            unit = kvargs.get("unit", None)
            if unit is None:
                raise ValueError("Invalid Wait arguments. Unit is not valid")
            self.duration_end_time = get_duration_end(self.engine._tick_time, time, unit)
        else:
            raise ValueError("Invalid Wait arguments. A duration is required")

    def _run(self):
        self.engine._runstate_waiting = True

        while self.engine._tick_time < self.duration_end_time:
            yield

        self.engine._runstate_waiting = False


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

            e.tag_context.emit_on_stop()

            e._set_run_id("empty")
            e._stop_interpreter()
            logger.info("Restarting engine - engine stopped")

            yield

            logger.info("Restarting engine - starting engine")
            # potentially a lot more engine state to reset
            e._runstate_started = True
            e._runstate_started_time = time.time()
            e._runstate_paused = False
            e._runstate_holding = False
            e._system_tags[SystemTagName.BLOCK_TIME].set_value(0.0, e._tick_time)
            e.block_times.clear()  # kinda hackish, tag should be self-contained

            e.tag_context.emit_on_start()

            e._set_run_id("new")
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)
            logger.info("Restarting engine complete")


class InfoEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.INFO)

    def _run(self):
        msg = self.kvargs.get("unparsed_args")
        logger.info(f"Info: {msg}")


class WarningEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.WARNING)

    def _run(self):
        msg = self.kvargs.get("unparsed_args")
        logger.warning(f"Warning: {msg}")


class ErrorEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine) -> None:
        super().__init__(EngineCommandEnum.ERROR)

    def _run(self):
        msg = self.kvargs.get("unparsed_args")
        logger.error(f"Error: {msg}")
