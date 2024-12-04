from __future__ import annotations
import itertools
import logging
import uuid
from queue import Empty, Queue
from typing import Iterable, List, Literal, Set
from uuid import UUID
from openpectus.engine.internal_commands import (
    create_internal_command,
    get_running_internal_command,
    dispose_command_map,
    register_commands
)
from openpectus.engine.hardware import HardwareLayerException, RegisterDirection
from openpectus.engine.method_model import MethodModel
from openpectus.engine.models import MethodStatusEnum, SystemStateEnum, EngineCommandEnum, SystemTagName
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.clock import Clock, WallClock
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.errors import (
    EngineError, EngineNotInitializedError, InterpretationError, InterpretationInternalError
)
from openpectus.lang.exec.pinterpreter import PInterpreter, InterpreterContext
from openpectus.lang.exec.runlog import RuntimeInfo, RunLog, RuntimeRecord, RuntimeRecordStateEnum
from openpectus.lang.exec.tag_lifetime import TagContext
from openpectus.lang.exec.tags import (
    Tag,
    TagCollection,
    TagDirection,
    TagValue,
    TagValueCollection,
    ChangeListener,
    Unset,
)
from openpectus.lang.exec.tags_impl import MarkTag
from openpectus.lang.exec.timer import EngineTimer, OneThreadTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram
import openpectus.protocol.models as Mdl
from openpectus.engine.archiver import ArchiverTag

logger = logging.getLogger(__name__)
frontend_logger = logging.getLogger(__name__ + ".frontend")

class EngineTiming():
    """ Represents timing information used by engine and any related components. """
    def __init__(self, clock: Clock, timer: EngineTimer, interval: float, speed: float) -> None:
        self._clock = clock
        self._timer = timer
        self._interval = interval
        self._speed = speed

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

        register_commands(self)

        self._clock: Clock = timing.clock
        """ The time source """

        self._tick_timer: EngineTimer = timing.timer
        """ Timer that invokes tick() """

        self._tick_time: float = 0.0
        """ The time of the last tick """
        self._tick_number: int = -1
        """ Tick count since last START command. It is incremented at the start of each tick.
        First tick is effectively number 0. """

        self._system_tags = TagCollection.create_system_tags()
        self._system_tags.add(MarkTag())
        # Add archiver which is implemented as a tag. The lambda getting the runlog works because the
        # tag_lifetime.on_stop event is emitted just before resetting the interpreter and runlog (and
        # not after).
        if enable_archiver:
            archiver = ArchiverTag(lambda : self.runtimeinfo.get_runlog(), self.uod.data_log_interval_seconds)
            self._system_tags.add(archiver)

        self.uod.system_tags = self._system_tags

        self.cmd_queue: Queue[CommandRequest] = Queue()
        """ Commands to execute, coming from interpreter and from aggregator """
        self.cmd_executing: List[CommandRequest] = []
        """ Uod commands currently being excuted """
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
        self._runstate_waiting: bool = False
        """ Indicates whether the engine is waiting in a Wait command"""

        self._prev_state: TagValueCollection | None = None
        """ The state prior to applying safe state """

        self._last_error : Exception | None = None
        """ Cause of error_state"""

        self.block_times: dict[str, float] = {}
        """ holds time spent in each block"""

        self._tags: TagCollection | None = None
        self._tag_context: TagContext | None = None

        self._interpreter: PInterpreter = PInterpreter(PProgram(), self)
        """ The interpreter executing the current program. """

        def on_method_init():
            self._interpreter.stop()
            self._interpreter = PInterpreter(self._method.get_program(), self)
            logger.info("Method and interpreter re-initialized")

        def on_method_error(ex: Exception):
            logger.error("An error occured while setting new method: " + str(ex))

        self._method: MethodModel = MethodModel(on_method_init, on_method_error)
        """ The model handling changes to program/method code """

        self._cancel_command_exec_ids: list[UUID] = []

    def _iter_all_tags(self) -> Iterable[Tag]:
        return itertools.chain(self._system_tags, self.uod.tags)

    def tags_as_readonly(self) -> TagValueCollection:
        return TagValueCollection(t.as_readonly() for t in self._iter_all_tags())

    @property
    def tags(self) -> TagCollection:
        if self._tags is None:
            raise EngineNotInitializedError("Tags not set")
        return self._tags

    @property
    def lifetime(self) -> TagContext:
        if self._tag_context is None:
            raise EngineNotInitializedError("TagContext not set")
        return self._tag_context

    @property
    def base_unit_provider(self) -> BaseUnitProvider:
        return self.uod.base_unit_provider

    @property
    def interpreter(self) -> PInterpreter:
        if self._interpreter is None:
            raise EngineNotInitializedError("No interpreter set")
        return self._interpreter

    @property
    def tag_context(self) -> TagContext:
        if self._tag_context is None:
            raise EngineNotInitializedError("Tag context not set")
        return self._tag_context

    @property
    def runtimeinfo(self) -> RuntimeInfo:
        return self.interpreter.runtimeinfo

    @property
    def method(self) -> MethodModel:
        return self._method

    def cleanup(self):
        if self._tag_context is not None:
            self.tag_context.emit_on_engine_shutdown()
        dispose_command_map()

    def get_runlog(self) -> RunLog:
        return self.runtimeinfo.get_runlog()

    def _configure(self):
        self.uod.tags.add_listener(self._uod_listener)
        self._system_tags.add_listener(self._system_listener)
        self._tags = self._system_tags.merge_with(self.uod.tags)
        self._tag_context = TagContext(self.tags)
        self._tick_timer.set_tick_fn(self.tick)

    def run(self, skip_timer_start=False):
        self._configure()
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

        self.tag_context.emit_on_engine_configured()

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

    def tick(self, tick_time: float, increment_time: float):
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

        # read, error_state on HardwareLayerException
        self.read_process_image()

        # excecute interpreter tick
        if self._runstate_started and\
                not self._runstate_paused and\
                not self._runstate_holding and\
                not self._runstate_waiting and\
                not self._runstate_stopping:
            try:
                # run one tick of interpretation, i.e. one instruction
                self._interpreter.tick(tick_time, self._tick_number)
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
        self.execute_commands()

        # notify of tag changes
        self.notify_tag_updates()

        # write, error_state on HardwareLayerException
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
        logger.debug(f"{increment_time = }")

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

        # Block name + signal block changes to tag_context
        block_name = self._system_tags[SystemTagName.BLOCK].get_value() or ""
        assert isinstance(block_name, str)

        # Block Time    - 0 at Block start, global but value refers to active block
        if block_name not in self.block_times.keys():
            self.block_times[block_name] = 0.0
        # TODO should probably increment all parent block timers as well.
        # In that case factor this out into BlockTag class that hold timer tags for each block
        self.block_times[block_name] += increment_time
        self._system_tags[SystemTagName.BLOCK_TIME].set_value(self.block_times[block_name], self._tick_time)

        # Execute the tick lifetime hook on tags
        self.tag_context.emit_on_tick(tick_time, increment_time)

    def execute_commands(self):
        done = False
        # add command request from incoming queue

        while self.cmd_queue.qsize() > 0 and not done:
            try:
                engine_command = self.cmd_queue.get()
                # Note: New commands are inserted at the beginning of the list.
                # This allows simpler cancellation of identical/overlapping commands
                self.cmd_executing.insert(0, engine_command)
            except Empty:
                done = True

        # execute a tick of each running command
        cmds_done: Set[CommandRequest] = set()
        latest_cmd = "(none)"
        try:
            for c in self.cmd_executing:
                latest_cmd = c.name
                if c not in cmds_done:
                    # Note: Executing one command may cause other commands to be cancelled (by identical or overlapping
                    # commands) Rather than modify self.cmd_executing (while iterating over it), cancelled/completed
                    # commands are added to the cmds_done set.
                    self._execute_command(c, cmds_done)
        except ValueError as ve:
            logger.error(f"Error executing command: '{latest_cmd}'. Command failed with error: {ve}", exc_info=True)
            frontend_logger.error(f"Command '{latest_cmd}' failed: {ve}")
            self.set_error_state(ve)
        except Exception as ex:
            logger.error(f"Error executing command: '{latest_cmd}'", exc_info=True)
            frontend_logger.error(f"Error executing command: '{latest_cmd}'")
            self.set_error_state(ex)
        finally:
            for c_done in cmds_done:
                self.cmd_executing.remove(c_done)

    def _execute_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        # execute an internal engine command or a uod command

        logger.debug("Executing command: " + cmd_request.name)
        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
            frontend_logger.error("Cannot execute command with empty name")
            cmds_done.add(cmd_request)
            return

        if EngineCommandEnum.has_value(cmd_request.name):
            self._execute_internal_command(cmd_request, cmds_done)
        else:
            self._execute_uod_command(cmd_request, cmds_done)

    def _execute_internal_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):

        if not self._runstate_started and cmd_request.name not in [EngineCommandEnum.START, EngineCommandEnum.RESTART]:
            logger.warning(f"Command {cmd_request.name} is invalid when Engine is not running")
            cmds_done.add(cmd_request)
            return

        # get the runtime record to use for tracking if possible
        record = RuntimeRecord.null_record()
        if cmd_request.exec_id is not None:  # happens for all commands not originating from interpreter
            # during restart, record is None - should ont occur otherwise
            record = self.interpreter.runtimeinfo.get_exec_record(cmd_request.exec_id)

        # an existing, long running engine_command is running. other commands must wait
        # Note: we need a priority mechanism - even Stop is waiting here
        command = get_running_internal_command()
        if command is not None:
            if cmd_request.name == command.name:
                if not command.is_finalized():
                    command.tick()
                if command.has_failed():
                    cmds_done.add(cmd_request)
                    if record is not None:
                        record.add_state_failed(self._tick_time, self._tick_number, self.tags_as_readonly())
                    else:
                        logger.error(f"Failed to record failed state for command {cmd_request}")
                elif command.is_finalized():
                    cmds_done.add(cmd_request)
                    if record is not None:
                        record.add_state_completed(self._tick_time, self._tick_number, self.tags_as_readonly())
                    else:
                        logger.error(f"Failed to record completed state for command {cmd_request}")
            return

        # no engine command is running - start one
        try:
            command = create_internal_command(cmd_request.name)
            args = cmd_request.get_args()
            if args is not None:
                try:
                    command.init_args(args)
                    logger.debug(f"Initialized command {cmd_request.name} with arguments {args}")
                except Exception:
                    raise EngineError(
                        f"Failed to initialize arguments '{args}' for command '{cmd_request.name}'",
                        "same"
                    )

        except ValueError:
            raise EngineError(
                f"Unknown internal engine command '{cmd_request.name}'",
                f"Unknown command '{cmd_request.name}'")

        if record is not None:
            record.add_state_started(self._tick_time, self._tick_number, self.tags_as_readonly())
            command.tick()
            if command.has_failed():
                record.add_state_failed(self._tick_time, self._tick_number, self.tags_as_readonly())
                cmds_done.add(cmd_request)
            elif command.is_finalized():
                record.add_state_completed(self._tick_time, self._tick_number, self.tags_as_readonly())
                cmds_done.add(cmd_request)
        else:
            logger.error(f"Runtime record is None for command {cmd_request}, this should not occur")

    def _set_run_id(self, op: Literal["new", "empty"]):
        if op == "new":
            self._system_tags[SystemTagName.RUN_ID].set_value(str(uuid.uuid4()), self._tick_time)
        elif op == "empty":
            self._system_tags[SystemTagName.RUN_ID].set_value(None, self._tick_time)

    def _stop_interpreter(self):
        self._interpreter.stop()
        self._interpreter = PInterpreter(self._method.get_program(), self)

    def _cancel_uod_commands(self):
        logger.debug("Cancelling uod commands")
        cmds_to_cancel: list[UodCommand] = []
        for name, command in self.uod.command_instances.items():
            if command.is_cancelled() or command.is_execution_complete() or command.is_finalized():
                logger.debug(f"Skipping command '{name}' that is no longer running")
            else:
                cmds_to_cancel.append(command)

        # remove outside the loop because cancel modifies the collection
        for command in cmds_to_cancel:
            command.cancel()

    def _execute_uod_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        cmd_name = cmd_request.name
        assert self.uod.has_command_name(cmd_name), f"Expected Uod to have command named '{cmd_name}'"
        assert cmd_request.exec_id is not None, f"Expected uod command request '{cmd_name}' to have exec_id"

        if not self.uod.hwl.is_connected:
            raise EngineError(
                f"The hardware is disconnected. The command '{cmd_name}' was not allowed to start.",
                "same")

        cancel_this = False

        # cancel any pending cancels (per user request)
        for c in self.cmd_executing:
            if c.command_exec_id in self._cancel_command_exec_ids:
                cmds_done.add(c)
                self._cancel_command_exec_ids.remove(c.command_exec_id)
                cmd_record = self.runtimeinfo.get_uod_command_and_record(c.command_exec_id)
                if cmd_record is not None:
                    command, c_record = cmd_record
                    command.cancel()
                    c_record.add_command_state_cancelled(
                        c.command_exec_id, self._tick_time, self._tick_number, self.tags_as_readonly())
                    logger.info(f"Running command {c.name} cancelled per user request")
                else:
                    logger.error(f"Cannot cancel command {c}. No runtime record found with {c.exec_id=}" +
                                 f" and {c.command_exec_id=}")
        if cmd_request.command_exec_id in self._cancel_command_exec_ids:
            self._cancel_command_exec_ids.remove(cmd_request.command_exec_id)
            cancel_this = True

        # cancel any existing instance with same name
        for c in [_c for _c in self.cmd_executing if _c not in cmds_done]:
            if c.name == cmd_name and not c == cmd_request:
                cmds_done.add(c)
                assert c.command_exec_id is not None, f"command_exec_id should be set for command '{cmd_name}'"
                cmd_record = self.runtimeinfo.get_uod_command_and_record(c.command_exec_id)
                assert cmd_record is not None
                command, c_record = cmd_record
                command.cancel()
                c_record.add_command_state_cancelled(
                    c.command_exec_id, self._tick_time, self._tick_number,
                    self.tags_as_readonly())
                logger.debug(f"Running command {c.name} cancelled because another was started")

        # cancel any overlapping instance
        for c in [_c for _c in self.cmd_executing if _c not in cmds_done]:
            if not c == cmd_request:
                for overlap_list in self.uod.overlapping_command_names_lists:
                    if c.name in overlap_list and cmd_name in overlap_list:
                        cmds_done.add(c)
                        assert c.command_exec_id is not None, f"command_exec_id should be set for command '{c.name}'"
                        cmd_record = self.runtimeinfo.get_uod_command_and_record(c.command_exec_id)
                        assert cmd_record is not None
                        command, c_record = cmd_record
                        command.cancel()
                        c_record.add_command_state_cancelled(
                            c.command_exec_id, self._tick_time, self._tick_number,
                            self.tags_as_readonly())
                        logger.info(
                            f"Running command {c.name} cancelled because overlapping command " +
                            f"'{cmd_name}' was started")
                        break

        if cancel_this:
            # don't start command again that was just cancelled
            return

        record = self.interpreter.runtimeinfo.get_exec_record(cmd_request.exec_id)
        if record is None:
            logger.error(f"Failed to get record for command {cmd_request}")
            return

        # create or get command instance
        if not self.uod.has_command_instance(cmd_name):
            uod_command = self.uod.create_command(cmd_name)
            cmd_request.command_exec_id = record.add_state_uod_command_set(
                uod_command,
                self._tick_time,
                self._tick_number,
                self.tags_as_readonly())
        else:
            uod_command = self.uod.get_command(cmd_name)

        assert uod_command is not None, f"Failed to get uod_command for command '{cmd_name}'"

        logger.debug(f"Parsing arguments '{cmd_request.unparsed_args}' for uod command {cmd_name}")
        parsed_args = uod_command.parse_args(cmd_request.unparsed_args or "")

        if parsed_args is None:
            logger.error(f"Invalid argument string: '{cmd_request.unparsed_args}' for command '{cmd_name}'")
            cmds_done.add(cmd_request)
            raise ValueError(f"Invalid arguments for command '{cmd_name}'")

        # execute command state flow
        try:
            logger.debug(
                f"Executing uod command: '{cmd_request.name}' with parsed args '{parsed_args}', " +
                f"iteration {uod_command._exec_iterations}")
            if uod_command.is_cancelled():
                if not uod_command.is_finalized():
                    cmds_done.add(cmd_request)
                    uod_command.finalize()

            if not uod_command.is_initialized():
                uod_command.initialize()
                logger.debug(f"Command {cmd_request.name} initialized")

            if not uod_command.is_execution_started():
                assert cmd_request.command_exec_id is not None
                record.add_command_state_started(
                    cmd_request.command_exec_id,
                    self._tick_time, self._tick_number,
                    self.tags_as_readonly())
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed first iteration {uod_command._exec_iterations}")
            elif not uod_command.is_execution_complete():
                uod_command.execute(parsed_args)
                logger.debug(f"Command {cmd_request.name} executed another iteration {uod_command._exec_iterations}")

            if uod_command.is_execution_complete() and not uod_command.is_finalized():
                assert cmd_request.command_exec_id is not None
                record.add_command_state_completed(
                    cmd_request.command_exec_id,
                    self._tick_time, self._tick_number,
                    self.tags_as_readonly())
                cmds_done.add(cmd_request)
                uod_command.finalize()
                logger.debug(f"Command {cmd_request.name} finalized")

        except Exception as ex:
            if cmd_request in self.cmd_executing:
                cmds_done.add(cmd_request)
            assert cmd_request.command_exec_id is not None
            record.add_command_state_failed(
                cmd_request.command_exec_id,
                self._tick_time, self._tick_number,
                self.tags_as_readonly())
            cmd_record = self.runtimeinfo.get_uod_command_and_record(cmd_request.command_exec_id)
            if cmd_record is not None:
                assert cmd_record[1].exec_id == record.exec_id
                command = cmd_record[0]
                if command is not None and not command.is_cancelled():
                    command.cancel()
                    logger.info(f"Cleaned up failed command {cmd_name}")

            logger.error(
                f"Uod command execution failed. Command: '{cmd_request.name}', " +
                f"argument string: '{cmd_request.unparsed_args}'", exc_info=True)
            raise ex

    def _apply_safe_state(self) -> TagValueCollection:
        current_values: List[TagValue] = []

        # TODO we should probably only consider uod tags here. would system tags ever have a safe value?
        for t in self._iter_all_tags():
            if t.direction == TagDirection.Output:
                safe_value = t.safe_value
                if not isinstance(safe_value, Unset):
                    current_values.append(t.as_readonly())
                    t.set_value(safe_value, self._tick_time)

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
                logger.warning(f'Setting a tick time on {tag.name} tag missing it in notify_initial_tags()')
                tag.tick_time = self._tick_time
            self.tag_updates.put(tag)

    def notify_tag_updates(self):
        """ Collect tag updates from tags modified since last cycle """
        # pick up changes from listeners and queue them up
        for tag_name in self._system_listener.changes:
            tag = self._system_tags[tag_name]
            self.tag_updates.put(tag)
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

    def has_error_state(self) -> bool:
        method_status = self._system_tags[SystemTagName.METHOD_STATUS]
        return method_status.get_value() == MethodStatusEnum.ERROR

    def get_error_state_exception(self) -> Exception | None:
        return self._last_error

    #TODO remove
    def parse_pcode(self, pcode: str) -> PProgram:
        p = PGrammar()
        p.parse(pcode)
        return p.build_model()

    def write_process_image(self):
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

    def schedule_execution(self, name: str, exec_id: UUID | None = None, **kvargs):
        """ Execute named command from interpreter """
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            request = CommandRequest.from_interpreter(name, exec_id, **kvargs)
            self.cmd_queue.put_nowait(request)
        else:
            raise EngineError(
                f"Invalid command type scheduled: '{name}'",
                f"Unknown command: '{name}'"
            )

    def schedule_execution_user(self, name: str, args: str | None = None):
        """ Execute named command from user """
        # TODO args format needs to be specified in more detail. Its intended usage is
        # to contain argument values added to tag buttons. But in that case why not just use pcode?
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            if args is not None:
                raise NotImplementedError("User arguments format not implemented - command name: " + name)
            request = CommandRequest.from_user(name)
            self.cmd_queue.put_nowait(request)
        else:
            logger.error(f"Invalid command type scheduled: '{name}'")
            frontend_logger.error(f"Unknown command: '{name}'")
            raise Exception(f"Invalid command type scheduled: '{name}'")

    def inject_code(self, pcode: str):
        """ Inject a code snippet to run in the current scope of the current program """
        # TODO review signal Method change
        # TODO perform this change via _method
        logger.warning("TODO set updated method content and signal Method change")
        try:
            injected_program = self.parse_pcode(pcode)
            self.interpreter.inject_node(injected_program)
            logger.info("Injected code successful")
        except Exception as ex:
            logger.info("Injected code parse error: " + str(ex))
            self.set_error_state(ex)
            raise

    # code manipulation api
    def set_method(self, method: Mdl.Method):
        """ Set new method. This will replace the current method and invoke the on_method_init callback.

        On error, sets error_state and re-raises the error.
        """
        try:
            self._method.set_method(method)
            logger.debug(f"New method set with {len(method.lines)} lines")
        except Exception as ex:
            logger.error("Failed to set method", exc_info=True)
            self.set_error_state(ex)
            raise

    def cancel_instruction(self, exec_id: UUID):
        # try exec_id as a record exec_id
        record = self.runtimeinfo.get_exec_record(exec_id=exec_id)
        if record is not None:
            logger.info(f"Cancelling instruction {exec_id=}")
            record.node.cancel()
        else:
            # try exec_id as a command_exec_id
            result = self.runtimeinfo.get_uod_command_and_record(command_exec_id=exec_id)
            if result is not None:
                _, record = result
                logger.info(f"Schedule cancellation of uod command {exec_id=}")
                self._cancel_command_exec_ids.append(exec_id)
                record.node.cancel()  # also need to mark the node as cancelled to update the runlog

        if record is None:
            logger.error(f"Cannot cancel instruction {exec_id=}, no runtime record exec_id or command_exec_id found")

    def force_instruction(self, exec_id: UUID):
        record = self.runtimeinfo.get_exec_record(exec_id=exec_id)
        if record is None:
            logger.error(f"Cannot force instruction {exec_id=}, no runtime record found")
        else:
            logger.info(f"Forcing instruction {exec_id=}")
            record.node.force()

    def calculate_method_state(self) -> Mdl.MethodState:
        return self._method.calculate_method_state(self.interpreter.runtimeinfo)
