from __future__ import annotations
import logging
import time

from openpectus.engine.internal_commands import InternalCommandsRegistry, InternalEngineCommand
from openpectus.engine.models import EngineCommandEnum, MethodStatusEnum, SystemStateEnum
from openpectus.lang.exec.argument_specification import command_argument_none, command_argument_regex
from openpectus.lang.exec.events import RunStateChange
from openpectus.lang.exec.regex import REGEX_DURATION_OPTIONAL, REGEX_TEXT, get_duration_end
from openpectus.lang.exec.tags import SystemTagName
from openpectus.engine.engine import Engine
from openpectus.lang.exec.units import as_float


logger = logging.getLogger(__name__)


CANCEL_TIMEOUT_TICKS = 10

# Note: Classes in this module are auto-registered as internal engine commands by
# InternalCommandsRegistry during engine initialization.


@command_argument_none()
class StartEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.START, registry)
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
            run_id = e.set_run_id()
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)
            e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)
            e._system_tags[SystemTagName.RUN_TIME].set_value(0.0, e._tick_time)
            e._system_tags[SystemTagName.PROCESS_TIME].set_value(0.0, e._tick_time)
            e._system_tags[SystemTagName.RUN_COUNTER].set_value(0, e._tick_time)

            e.emitter.emit_on_start(run_id)


@command_argument_regex(REGEX_DURATION_OPTIONAL)
class PauseEngineCommand(InternalEngineCommand):
    """ Pause execution of commands and time. Put output tags into safe state.

    See also Hold and Wait.
    """
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.PAUSE, registry)
        self.engine = engine

    def _run(self):
        duration_end_time : float | None = None
        time = as_float(self.kvargs.pop("number", ""))
        if time is not None:
            try:
                unit = self.kvargs.pop("number_unit")
            except Exception:
                raise ValueError(f"Argument error. Actual kvargs: {self.kvargs}")
            duration_end_time = get_duration_end(self.engine._tick_time, time, unit)

        e = self.engine
        e._runstate_paused = True
        e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Paused, e._tick_time)
        e._prev_state = e._apply_safe_state()
        e.emitter.emit_on_runstate_change(RunStateChange.PAUSE)

        if duration_end_time is not None:
            logger.debug("Pause duration set. Waiting to unpause.")
            while self.engine._tick_time < duration_end_time:
                yield
            logger.debug("Resuming using Unpause")
            UnpauseEngineCommand(self.engine, self._registry)._run()


@command_argument_none()
class UnpauseEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.UNPAUSE, registry)
        self.engine = engine

    def _run(self):
        e = self.engine

        e._runstate_paused = False
        sys_state_value = SystemStateEnum.Holding if e._runstate_holding else SystemStateEnum.Running
        e._system_tags[SystemTagName.SYSTEM_STATE].set_value(sys_state_value, e._tick_time)

        # pre-pause values are always applied on unpause, regardless of hold state.
        if e._prev_state is not None:
            e._apply_state(e._prev_state)
            e._prev_state = None
        else:
            logger.error("Failed to apply state prior to safe state. Prior state was not available")

        # Note: we currently don't have hold/unhold events to worry about here
        e.emitter.emit_on_runstate_change(RunStateChange.UNPAUSE)

        # TODO Consider how a corrected error should be handled. It depends on the cause
        # - Run time value is broken: Maybe trying again will fix it
        # - Code is broken and the user fixes it: The interpreter should resume from the error node
        # which can be complex and requires the full editing feature. For now, we just take the error
        # flag down and hope for the best
        e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)


@command_argument_regex(REGEX_DURATION_OPTIONAL)
class HoldEngineCommand(InternalEngineCommand):
    """ Hold execution of commands and time, keeping ouput tags in their current state.

    See also Pause and Wait.
    """
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.HOLD, registry)
        self.engine = engine

    def _run(self):
        duration_end_time : float | None = None
        time = as_float(self.kvargs.pop("number", ""))
        if time is not None:
            try:
                unit = self.kvargs.pop("number_unit")
            except Exception:
                raise ValueError(f"Argument error. Actual kvargs: {self.kvargs}")
            duration_end_time = get_duration_end(self.engine._tick_time, time, unit)

        e = self.engine
        e._runstate_holding = True
        if not e._runstate_paused:  # Pause takes precedence
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Holding, e._tick_time)

        if duration_end_time is not None:
            logger.debug("Hold duration set. Waiting to unhold.")
            while self.engine._tick_time < duration_end_time:
                yield
            logger.debug("Resuming using Unhold")
            UnholdEngineCommand(self.engine, self._registry)._run()


@command_argument_none()
class UnholdEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.UNHOLD, registry)
        self.engine = engine

    def _run(self):
        e = self.engine
        e._runstate_holding = False
        if not e._runstate_paused:  # Pause takes precedence
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)


@command_argument_none()
class StopEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.STOP, registry)
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
            yield
            timeout_at_tick = e._tick_number + CANCEL_TIMEOUT_TICKS
            while e.uod.has_any_command_instances():
                if e._tick_number > timeout_at_tick:
                    logger.warning("Timeout waiting for uod commands to cancel")
                    break
                yield
            e._finalize_uod_commands()

            logger.debug("All uod commands have completed execution. Stop will now complete.")
            e._runstate_started = False
            e._runstate_paused = False
            e._runstate_holding = False
            e._runstate_stopping = False
            e._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, e._tick_time)

            e.emitter.emit_on_stop()

            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, e._tick_time)
            e.clear_run_id()
            e._stop_interpreter()


@command_argument_none()
class RestartEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.RESTART, registry)
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
            yield
            timeout_at_tick = e._tick_number + CANCEL_TIMEOUT_TICKS
            while e.uod.has_any_command_instances():
                if e._tick_number > timeout_at_tick:
                    logger.warning("Timeout waiting for uod commands to cancel")
                    break
                yield
            e._finalize_uod_commands()

            logger.debug("Restarting engine - uod commands have completed execution")
            e._runstate_started = False
            e._runstate_paused = False
            e._runstate_holding = False
            e._runstate_stopping = False
            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, e._tick_time)

            e.emitter.emit_on_stop()

            e.clear_run_id()
            e._stop_interpreter()
            logger.info("Restarting engine - engine stopped")

            yield

            logger.info("Restarting engine - starting engine")
            # potentially a lot more engine state to reset
            e._runstate_started = True
            e._runstate_started_time = time.time()
            e._runstate_paused = False
            e._runstate_holding = False

            run_id = e.set_run_id()
            e.emitter.emit_on_start(run_id)

            e._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, e._tick_time)
            logger.info("Restarting engine complete")


@command_argument_regex(REGEX_TEXT)
class InfoEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.INFO, registry)

    def _run(self):
        msg = self.kvargs.get("text")
        logger.info(f"Info: {msg}")


@command_argument_regex(REGEX_TEXT)
class WarningEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.WARNING, registry)

    def _run(self):
        msg = self.kvargs.get("text")
        logger.warning(f"Warning: {msg}")


@command_argument_regex(REGEX_TEXT)
class ErrorEngineCommand(InternalEngineCommand):
    def __init__(self, engine: Engine, registry: InternalCommandsRegistry) -> None:
        super().__init__(EngineCommandEnum.ERROR, registry)

    def _run(self):
        msg = self.kvargs.get("text")
        logger.error(f"Error: {msg}")
