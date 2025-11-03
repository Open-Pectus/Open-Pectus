from __future__ import annotations

import itertools
import logging
from threading import Lock
import uuid
from queue import Queue
from typing import Iterable, Literal

from openpectus.engine.command_manager import CommandManager
import openpectus.protocol.models as Mdl
from openpectus.engine.archiver import ArchiverTag
from openpectus.engine.hardware import HardwareLayerException, RegisterDirection
from openpectus.engine.internal_commands import InternalCommandsRegistry
from openpectus.engine.method_manager import MethodManager
from openpectus.engine.models import MethodStatusEnum, SystemStateEnum, EngineCommandEnum, SystemTagName
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.clock import Clock, WallClock
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.errors import (
    EngineError, EngineNotInitializedError, InterpretationError, InterpretationInternalError, MethodEditError
)
from openpectus.lang.exec.events import EventEmitter
from openpectus.lang.exec.pinterpreter import PInterpreter, InterpreterContext, Tracking
from openpectus.lang.exec.tags import (
    Tag,
    TagCollection,
    TagValue,
    TagValueCollection,
    ChangeListener,
    create_system_tags
)
from openpectus.lang.exec.tags_impl import BlockTimeTag, MarkTag, ScopeTimeTag
from openpectus.lang.exec.timer import EngineTimer, OneThreadTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase

logger = logging.getLogger(__name__)
frontend_logger = logging.getLogger(__name__ + ".frontend")


class EngineTiming():
    """ Represents timing information used by engine and any related components. """

    def __init__(self, clock: Clock, timer: EngineTimer, interval: float, speed: float) -> None:
        self._clock = clock
        self._timer = timer
        self._interval = interval
        self._speed = speed

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(_clock="{self._clock}", _timer={self._timer}, ' +
                f'_interval={self._interval}, _speed={self._speed})')

    @staticmethod
    def default() -> EngineTiming:
        return EngineTiming(WallClock(), OneThreadTimer(0.1, None), 0.1, 1.0)

    @property
    def clock(self) -> Clock:
        return self._clock

    @property
    def timer(self) -> EngineTimer:
        return self._timer

    @property
    def interval(self) -> float:
        return self._interval

    @property
    def speed(self) -> float:
        return self._speed


class Engine(InterpreterContext):
    """ Main engine class. Handles
    - io loop, reads and writes hardware process image (sync)
    - invokes interpreter to interpret next instruction (sync, generator based)
    - signals state changes via tag_updates queue (to EngineReporter)
    - accepts commands from cmd_queue (from interpreter and from aggregator)
    """

    def __init__(
            self,
            uod: UnitOperationDefinitionBase,
            timing: EngineTiming = EngineTiming.default(),
            enable_archiver=False) -> None:
        self.uod = uod
        self._running: bool = False
        """ Indicates whether the scan cycle loop is running, set to False to shut down"""

        self.registry = InternalCommandsRegistry(self).__enter__()
        """ Manages internal engine commands """

        self._clock: Clock = timing.clock
        """ The time source """

        self._tick_timer: EngineTimer = timing.timer
        """ Timer that invokes tick() """

        self._tick_time: float = 0.0
        """ The time of the last tick """
        self._tick_number: int = -1
        """ Tick count since last START command. It is incremented at the start of each tick.
        First tick is effectively number 0. """

        self._system_tags = create_system_tags()
        self._system_tags.add(MarkTag())
        self._system_tags.add(BlockTimeTag())
        self._system_tags.add(ScopeTimeTag())
        # Add archiver which is implemented as a tag. The lambda getting the runlog works because the
        # tag_lifetime.on_stop event is emitted just before resetting the interpreter and runlog (and
        # not after).
        if enable_archiver:
            archiver = ArchiverTag(
                lambda : self.tracking.get_runlog(),
                lambda : self.tags,
                self.uod.data_log_interval_seconds)
            self._system_tags.add(archiver)

        self.uod.system_tags = self._system_tags

        self.tag_updates: Queue[Tag] = Queue()
        """ Tags updated in last tick """

        self._uod_listener = ChangeListener()
        self._system_listener = ChangeListener()

        self._runstate_started: bool = False
        """ Indicates the current Start/Stop state"""
        self._runstate_started_time: float = 0
        """ Indicates the time of the last Start state"""
        self._runstate_paused: bool = False
        """ Indicates whether the engine is paused"""
        self._runstate_holding: bool = False
        """ Indicates whether the engine is on hold"""
        self._runstate_stopping: bool = False
        """ Indicates whether the engine is on stopping"""

        self._prev_state: TagValueCollection | None = None
        """ The state prior to applying safe state """

        self._last_error: Exception | None = None
        """ Cause of error_state"""

        # initialize state
        self.uod.tags.add_listener(self._uod_listener)
        self._system_tags.add_listener(self._system_listener)
        self._tags = self._system_tags.merge_with(self.uod.tags)
        self._emitter = EventEmitter(self._tags)
        self._tick_timer.set_tick_fn(self.tick)

        # there attributes must be declared before self.on_interpreter_reset() can use them
        self._interpreter: PInterpreter | None = None
        self._tracking: Tracking | None = None
        self._command_manager: CommandManager | None = None

        self._method_manager: MethodManager = MethodManager(uod.get_command_names(), self, self.on_interpreter_reset)
        """ The model handling changes to method code and interpreter running it """

        self._lock = Lock()


    def on_interpreter_reset(self, interpreter: PInterpreter):
        self._interpreter = interpreter
        self._tracking = interpreter.tracking
        restart_request_pending = None if self._command_manager is None else self._command_manager.restart_request_pending
        self._command_manager = CommandManager(self._tracking, self.uod, self.registry, restart_request_pending)

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(uod={self.uod}, is_running={self.is_running}, ' +
                f'has_error_state={self.has_error_state})')

    def _iter_all_tags(self) -> Iterable[Tag]:
        return itertools.chain(self._system_tags, self.uod.tags)

    def tags_as_readonly(self) -> TagValueCollection:
        return TagValueCollection(t.as_readonly() for t in self._iter_all_tags())

    @property
    def tags(self) -> TagCollection:
        return self._tags

    @property
    def emitter(self) -> EventEmitter:
        return self._emitter

    @property
    def base_unit_provider(self) -> BaseUnitProvider:
        return self.uod.base_unit_provider

    @property
    def method_manager(self) -> MethodManager:
        return self._method_manager

    @property
    def interpreter(self) -> PInterpreter:
        if self._interpreter is None:
            raise EngineNotInitializedError("interpreter not set")
        return self._interpreter

    @property
    def tracking(self) -> Tracking:
        if self._tracking is None:
            raise EngineNotInitializedError("tracking not set")
        return self._tracking

    def cleanup(self):
        self.emitter.emit_on_engine_shutdown()
        self.registry.__exit__(None, None, None)

    def run(self, skip_timer_start=False):
        self._run(skip_timer_start)

    def is_running(self) -> bool:
        return self._running

    def _run(self, skip_timer_start=True):
        """ Starts the scan cycle """

        assert self.uod is not None
        assert self.uod.hwl is not None
        assert self.uod.hwl.is_connected, "Hardware is not connected. Engine cannot start"

        self._running = True
        if not skip_timer_start:
            self._tick_timer.start()

        self.emitter.emit_on_engine_configured()

        # On engine start, write safe output values to hardware to bring hw to a known state
        self._apply_safe_state()
        self.write_process_image()

    def stop(self):
        logger.info("Engine shutting down")
        try:
            self.uod.hwl.disconnect()
        except HardwareLayerException:
            logger.error("Disconnect hardware error", exc_info=True)

        self._running = False
        self._tick_timer.stop()
        self.cleanup()

    def tick(self, tick_time: float, increment_time: float):  # noqa C901
        """ Performs a scan cycle tick. """
        # logger.debug(f"Tick {self._tick_number + 1}")

        if not self._running:
            self._tick_timer.stop()

        self._tick_time = tick_time
        self._tick_number += 1

        # Perform certain actions in first tick
        if self._tick_number == 0:
            # System tags are initialized before first tick, without a tick time, and some are never updated, so
            # provide first tick time as a "default".
            for tag in self._system_tags.tags.values():
                tag.tick_time = tick_time

        self.uod.hwl.tick()

        # read phase, error_state on HardwareLayerException
        self.read_process_image()

        # execute phase
        with self._lock:
            self.tracking.tick(tick_time, self._tick_number)

            # excecute interpreter tick
            if self._runstate_started and \
                    not self._runstate_paused and \
                    not self._runstate_holding and \
                    not self._runstate_stopping:
                try:
                    # run one tick of interpretation, i.e. one instruction
                    self.interpreter.tick(tick_time, self._tick_number)
                except InterpretationInternalError as ex:
                    logger.fatal("A serious internal interpreter error occured. The method should be stopped. If it is resumed, \
                                additional errors may occur.", exc_info=True)
                    self.set_error_state(ex)
                except EngineError as eex:
                    logger.error(eex.message)
                    if eex.user_message is not None:
                        frontend_logger.error(eex.user_message)
                    self.set_error_state(eex)
                except InterpretationError as ie:
                    logger.error("Interpretation error", exc_info=True)
                    if ie.user_message is not None:
                        frontend_logger.error(ie.user_message)
                    self.set_error_state(ie)
                except Exception as ex:
                    logger.error("Unhandled interpretation error", exc_info=True)
                    frontend_logger.error("Method error")
                    self.set_error_state(ex)

            # update calculated tags
            if self._runstate_started:
                self.update_calculated_tags(tick_time, increment_time)

            # execute queued commands, go to error_state on error
            try:
                assert self._command_manager is not None
                self._command_manager.tick(tick_time, self._tick_number)
            except Exception as ex:
                self.set_error_state(ex)

            # notify of tag changes
            self.notify_tag_updates()

            # write phase, error_state on HardwareLayerException
            self.write_process_image()

    def read_process_image(self):
        """ Read data from relevant hw registers into tags"""
        read_registers = [r for r in self.uod.hwl.registers.values() if RegisterDirection.Read in r.direction]
        try:
            # possibly add guard for ConnectionState=Disconnected to avoid read errors
            # flooding the log
            register_values = self.uod.hwl.read_batch(read_registers)
        except HardwareLayerException as ex:
            if not self.has_error_state():
                logger.error("Hardware read_batch error", exc_info=True)
                self.set_error_state(ex)
            return

        for i, r in enumerate(read_registers):
            tag = self.uod.tags.get(r.name)
            tag_value = register_values[i]
            if "to_tag" in r.options:
                tag_value = r.options["to_tag"](tag_value)
            tag.set_value(tag_value, self._tick_time)

    def update_calculated_tags(self, tick_time: float, increment_time: float):
        sys_state = self._system_tags[SystemTagName.SYSTEM_STATE]
        logger.debug(f"{increment_time=}")

        # Clock         - seconds since epoch
        clock = self._system_tags.get(SystemTagName.CLOCK)
        clock.set_value(tick_time, tick_time)

        # Process Time  - 0 at start, increments when System State is Run
        process_time = self._system_tags[SystemTagName.PROCESS_TIME]
        process_time_value = process_time.as_number()
        if sys_state.get_value() == SystemStateEnum.Running:
            process_time.set_value(process_time_value + increment_time, tick_time)

        # Run Time      - 0 at start, increments when System State is not Stopped
        run_time = self._system_tags[SystemTagName.RUN_TIME]
        run_time_value = run_time.as_number()
        if sys_state.get_value() not in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
            run_time.set_value(run_time_value + increment_time, tick_time)

        # Execute the tick lifetime hook on tags
        self.emitter.emit_on_tick(tick_time, increment_time)

    def set_run_id(self) -> str:
        """ Creates a new run_id, sets the Run Id tag to it and returns it. """
        run_id = str(uuid.uuid4())
        self._system_tags[SystemTagName.RUN_ID].set_value(run_id, self._tick_time)
        return run_id

    def clear_run_id(self):
        self._system_tags[SystemTagName.RUN_ID].set_value(None, self._tick_time)

    def _stop_interpreter(self):
        # called from Stop and Restart

        # does not seem necessary if calling reset_interpreter() below but it is
        self.interpreter.stop()

        # TODO: This hack reproduces the behavior of setting new interpreter
        # a few tests related to start/stop/restart depend on this - but it is not
        # clear whether this is a real requirement or not. In fact it may make more
        # sense to wait until start
        self.method_manager.reset_interpreter()

    def _apply_safe_state(self) -> TagValueCollection:
        current_values: list[TagValue] = []
        hwl = self.uod.hwl
        registers = [r for r in hwl.registers.values()
                     if RegisterDirection.Write in r.direction and "safe_value" in r._options]
        for r in registers:
            tag = self.uod.tags[r.name]
            current_values.append(tag.as_readonly())
            tag.set_value(r._options["safe_value"], self._tick_time)
        return TagValueCollection(current_values)

    def _apply_state(self, state: TagValueCollection):
        for t in self._iter_all_tags():
            if state.has(t.name):
                tag_value = state.get(t.name)
                t.set_value(tag_value.value, self._tick_time)

    def notify_all_tags(self):
        """ Collect tag updates from all tags, even unmodified tags """
        for tag in self._iter_all_tags():
            if tag.tick_time is None:
                logger.warning(f'Setting a tick time on {tag.name} tag missing it in notify_all_tags()')
                tag.tick_time = self._tick_time
            self.tag_updates.put(tag)

    def notify_tag_updates(self):
        """ Collect tag updates from tags modified since last cycle """
        # pick up changes from listeners and queue them up
        for tag_name in self._system_listener.changes:
            tag = self._system_tags[tag_name]
            self.tag_updates.put(tag)
            if tag_name == SystemTagName.CONNECTION_STATUS:
                status = self._system_tags[SystemTagName.CONNECTION_STATUS].get_value()
                assert isinstance(status, str)
                assert status == "Disconnected" or status == "Connected"
                self._emitter.emit_on_connection_status_change(status)
        self._system_listener.clear_changes()

        for tag_name in self._uod_listener.changes:
            tag = self.uod.tags[tag_name]
            self.tag_updates.put(tag)
        self._uod_listener.clear_changes()

    def set_error_state(self, exception: Exception):
        logger.info("Engine Paused because of error")
        self._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.ERROR, self._tick_time)
        self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Paused, self._tick_time)
        self._last_error = exception
        self._runstate_paused = True
        self._emitter.emit_on_method_error(exception)

    def has_error_state(self) -> bool:
        return self._last_error is not None

    def get_error_state_exception(self) -> Exception | None:
        return self._last_error

    def clear_error_state(self):
        self._last_error = None
        self._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.OK, self._tick_time)

    def write_process_image(self):
        if not self._runstate_started:
            return

        hwl = self.uod.hwl
        register_values = []
        registers = [r for r in hwl.registers.values() if RegisterDirection.Write in r.direction]
        for r in registers:
            tag_value = self.uod.tags[r.name].get_value()
            register_value = tag_value if "from_tag" not in r.options \
                else r.options["from_tag"](tag_value)
            register_values.append(register_value)
        try:
            # possibly add guard for ConnectionState=Disconnected to avoid write errors
            # flooding the log
            hwl.write_batch(register_values, registers)
        except HardwareLayerException as ex:
            if not self.has_error_state():
                logger.error("Hardware write_batch error", exc_info=True)
                self.set_error_state(ex)

    def schedule_execution(self, name: str, arguments: str = "", instance_id: str | None = None):
        """ Execute named command from interpreter """
        assert self._command_manager is not None
        if instance_id is None:
            instance_id = self.tracking.create_instance_id(name)
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            request = CommandRequest.from_interpreter(name, arguments, instance_id)
            self._command_manager.schedule(request)
        else:
            raise EngineError(
                f"Invalid command type scheduled: '{name}'",
                f"Unknown command: '{name}'"
            )

    def _validate_control_command(self, command_name: str):
        """ Raise a ValueError if the command is a control command that is not valid in the current
        engine state. """
        sys_state_value = self._system_tags[SystemTagName.SYSTEM_STATE].get_value()
        if command_name == EngineCommandEnum.START:
            if sys_state_value != SystemStateEnum.Stopped:
                raise ValueError(
                    f"Start command is only valid when system state is stopped. Current state is {sys_state_value}")
        elif command_name == EngineCommandEnum.STOP:
            if sys_state_value in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
                raise ValueError(f"Stop command is not valid when system state is {sys_state_value}")
        elif command_name == EngineCommandEnum.RESTART:
            if sys_state_value in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
                raise ValueError(f"Restart command is not valid when system state is {sys_state_value}")
        elif command_name == EngineCommandEnum.PAUSE:
            if sys_state_value in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
                raise ValueError(f"Pause command is not valid when system state is {sys_state_value}")
            if self._runstate_paused:
                raise ValueError("Pause command is not valid when system state is paused")
        elif command_name == EngineCommandEnum.UNPAUSE:
            if sys_state_value in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
                raise ValueError(f"Unpause command is not valid when system state is {sys_state_value}")
            if not self._runstate_paused:
                raise ValueError("Unpause command is not valid when system state is not paused")
        elif command_name == EngineCommandEnum.HOLD:
            if sys_state_value in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
                raise ValueError(f"Hold command is not valid when system state is {sys_state_value}")
            if self._runstate_holding:
                raise ValueError("Hold command is not valid when system state is on hold")
        elif command_name == EngineCommandEnum.UNHOLD:
            if sys_state_value in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
                raise ValueError(f"Unhold command is not valid when system state is {sys_state_value}")
            if not self._runstate_holding:
                raise ValueError("Unhold command is not valid when system state is not on hold")

    def execute_control_command_from_user(self, name: str):
        """ Execute named command from user """
        assert self._command_manager is not None
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            self._validate_control_command(name)
            request = CommandRequest.from_user(name, "", self.tracking.create_instance_id(name))
            self._command_manager.schedule(request)
        else:
            logger.error(f"Invalid command type scheduled: '{name}'")
            frontend_logger.error(f"Unknown command: '{name}'")
            raise Exception(f"Invalid command type scheduled: '{name}'")

    def inject_code(self, pcode: str):
        """ Inject a code snippet to run in the current scope of the current program """
        try:
            injected_program = self._method_manager.parse_inject_code(pcode)
            self.interpreter.inject_node(injected_program)
            logger.info("Injected code successful")
        except Exception as ex:
            logger.info("Injected code parse error: " + str(ex))
            self.set_error_state(ex)
            raise

    # Code manipulation api
    def set_method(self, method: Mdl.Method) -> Literal["merge_method", "set_method"]:
        """ Set new method. This will replace the current method, either by merging in changes in case the method is already
        running or just setting the method otherwise. """

        try:
            if self._runstate_started and self.method_manager.program_is_started:
                logger.info(f"Method changed while running. Current revision {self.method_manager.program.revision}")
                try:
                    self._method_manager.merge_method(method)
                    logger.info(f"Method merged successfully. Revision is now {self.method_manager.program.revision}")

                    # consider the edit an attempt to fix error state
                    if self.has_error_state():
                        self.clear_error_state()

                    return "merge_method"
                except Exception:
                    logger.error("Error merging method")
                    raise
            else:
                logger.info("Setting new method")
                try:
                    self._method_manager.set_method(method)
                    logger.info(f"Method set successfully. Revision is {self.method_manager.program.revision}")
                    return "set_method"
                except Exception:
                    logger.error("Error setting method")
                    raise

        except MethodEditError:
            # skip setting error_state(?) tests expects this and fails on error_state
            # depends on how we will handle these errors on the client side
            raise
        except Exception as ex:
            logger.error("Failed to set method", exc_info=True)
            logger.error(f"Current method content:\n\n{self.method_manager._method}\n")
            logger.error(f"New method content:\n\n{method}\n")
            self.set_error_state(ex)
            raise

    # Cancel/Force commands from user, originating from runlog item - lock should be used here, right?
    def cancel_instruction(self, instance_id: str):
        """ Cancel command instance and finalize it immidiately """
        with self._lock:
            assert self._command_manager is not None
            self._command_manager.cancel_instruction(instance_id)

    def force_instruction(self, instance_id: str):
        """ Force the command instance """
        with self._lock:
            assert self._command_manager is not None
            self._command_manager.force_instruction(instance_id)

    # Cancel/Finalize originating from Stop/Restart commands, i.e. from the tick commands loop
    def cancel_all_commands(self, source_command_name: str):
        assert self._command_manager is not None
        self._command_manager.cancel_commands(source_command_name, finalize=True)

    # This is unnecessary until we support a cancellation cool-down period
    # def finalize_all_commands(self, source_command_name: str):
    #     self._command_manager.finalize_commands(source_command_name)

    def get_command_definitions(self) -> list[Mdl.CommandDefinition]:
        """ Return engine command definitions. """
        return self.registry.get_command_definitions()
