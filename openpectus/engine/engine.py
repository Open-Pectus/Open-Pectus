import itertools
import logging
import time
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
from openpectus.engine.models import ConnectionStatusEnum, MethodStatusEnum, SystemStateEnum, EngineCommandEnum, SystemTagName
from openpectus.lang.exec.base_unit import BaseUnitProvider
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.errors import EngineNotInitializedError, InterpretationError, InterpretationInternalError
from openpectus.lang.exec.pinterpreter import PInterpreter, InterpreterContext
from openpectus.lang.exec.runlog import RuntimeInfo, RunLog, RuntimeRecord
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
from openpectus.lang.exec.timer import EngineTimer, OneThreadTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram
import openpectus.protocol.models as Mdl


logger = logging.getLogger(__name__)


class Engine(InterpreterContext):
    """ Main engine class. Handles
    - io loop, reads and writes hardware process image (sync)
    - invokes interpreter to interpret next instruction (sync, generator based)
    - signals state changes via tag_updates queue (to EngineReporter)
    - accepts commands from cmd_queue (from interpreter and from aggregator)
    """

    def __init__(self, uod: UnitOperationDefinitionBase, tick_interval=0.1) -> None:
        self.uod = uod
        self._running: bool = False
        """ Indicates whether the scan cycle loop is running, set to False to shut down"""

        register_commands(self)

        self._tick_time: float = 0.0
        """ The time of the last tick """
        self._tick_number: int = -1
        """ Tick count since last START command. It is incremented at the start of each tick.
        First tick is effectively number 0. """

        self._system_tags = TagCollection.create_system_tags()
        self.uod.system_tags = self._system_tags

        self.cmd_queue: Queue[CommandRequest] = Queue()
        """ Commands to execute, coming from interpreter and from aggregator """
        self.cmd_executing: List[CommandRequest] = []
        """ Uod commands currently being excuted """
        self.tag_updates: Queue[Tag] = Queue()
        """ Tags updated in last tick """

        self._uod_listener = ChangeListener()
        self._system_listener = ChangeListener()
        self._tick_timer: EngineTimer = OneThreadTimer(tick_interval, self.tick)

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

        self.block_times: dict[str, float] = {}
        """ holds time spent in each block"""

        self._tags: TagCollection | None = None
        self._tag_context: TagContext | None = None

        self.block_popped: str | None = None
        self.block_pushed: str | None = None

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
    def base_unit_provider(self) -> BaseUnitProvider:
        return self.uod.base_unit_provider

    def block_started(self, name: str):
        self.block_pushed = name
        self.block_popped = None

    def block_ended(self, name: str, new_name: str):
        self.block_pushed = new_name
        self.block_popped = name

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

    def run(self):
        self._configure()
        self._run()

    def is_running(self) -> bool:
        return self._running

    def _run(self):
        """ Starts the scan cycle """

        assert self.uod is not None
        assert self.uod.hwl is not None
        assert self.uod.hwl.is_connected, "Hardware is not connected. Engine cannot start"

        self._running = True
        self._tick_timer.start()

        self.tag_context.emit_on_engine_configured()

    def stop(self):
        logger.info("Engine shutting down")
        try:
            self.uod.hwl.disconnect()
        except HardwareLayerException:
            logger.error("Disconnect hardware error", exc_info=True)

        self._running = False
        self._tick_timer.stop()
        self.cleanup()

    def tick(self):
        """ Performs a scan cycle tick. """
        logger.debug(f"Tick {self._tick_number + 1}")

        if not self._running:
            self._tick_timer.stop()
            # TODO shutdown

        last_tick_time = self._tick_time
        self._tick_time = time.time()
        self._tick_number += 1

        # Perform certain actions in first tick
        if self._tick_number == 0:
            # System tags are initialized before first tick, without a tick time, and some are never updated, so
            # provide first tick time as a "default".
            for tag in self._system_tags.tags.values():
                tag.tick_time = self._tick_time

        self.uod.hwl.tick()

        # read
        self.read_process_image()

        # excecute interpreter tick
        if self._runstate_started and\
                not self._runstate_paused and\
                not self._runstate_holding and\
                not self._runstate_waiting and\
                not self._runstate_stopping:
            try:
                self._interpreter.tick(self._tick_time, self._tick_number)
            except InterpretationInternalError:
                logger.fatal("A serious internal interpreter error occured. The method should be stopped. If it is resumed, \
                             additional errors may occur.", exc_info=True)
                self.set_error_state()
            except InterpretationError:
                logger.error("Interpretation error", exc_info=True)
                self.set_error_state()
            except Exception:
                logger.error("Unhandled interpretation error", exc_info=True)
                self.set_error_state()

        # update calculated tags
        if self._runstate_started:
            self.update_calculated_tags(last_tick_time)

        # execute queued commands
        self.execute_commands()

        # notify of tag changes
        self.notify_tag_updates()

        # write
        self.write_process_image()

    def read_process_image(self):
        """ Read data from relevant hw registers into tags"""
        registers = [r for r in self.uod.hwl.registers.values() if RegisterDirection.Read in r.direction]
        try:
            register_values = self.uod.hwl.read_batch(registers)
        except HardwareLayerException:
            logger.error("Hardware read_batch error", exc_info=True)
            self.stop()
            return

        for i, r in enumerate(registers):
            tag = self.uod.tags.get(r.name)
            tag_value = register_values[i]
            if "to_tag" in r.options:
                tag_value = r.options["to_tag"](tag_value)
            tag.set_value(tag_value, self._tick_time)

    def update_calculated_tags(self, last_tick_time: float):
        sys_state = self._system_tags[SystemTagName.SYSTEM_STATE]
        time_increment = self._tick_time - last_tick_time if last_tick_time > 0.0 else 0.0
        logger.debug(f"{time_increment = }")

        # Clock         - seconds since epoch
        clock = self._system_tags.get(SystemTagName.CLOCK)
        clock.set_value(time.time(), self._tick_time)

        # Process Time  - 0 at start, increments when System State is Run
        process_time = self._system_tags[SystemTagName.PROCESS_TIME]
        process_time_value = process_time.as_number()
        if sys_state.get_value() == SystemStateEnum.Running:
            process_time.set_value(process_time_value + time_increment, self._tick_time)

        # Run Time      - 0 at start, increments when System State is not Stopped
        run_time = self._system_tags[SystemTagName.RUN_TIME]
        run_time_value = run_time.as_number()
        if sys_state.get_value() not in [SystemStateEnum.Stopped, SystemStateEnum.Restarting]:
            run_time.set_value(run_time_value + time_increment, self._tick_time)

        # Block name + signal block changes to tag_context
        block_name = self._system_tags[SystemTagName.BLOCK].get_value() or ""
        assert isinstance(block_name, str)
        if self.block_pushed is not None and self.block_popped is not None:
            block_name, old_block_name = self.block_pushed, self.block_popped
            self.block_popped, self.block_pushed = None, None
            self.tag_context.emit_on_block_end(old_block_name, block_name, self._tick_number)
        elif self.block_pushed is not None:
            block_name = self.block_pushed
            self.block_pushed = None
            self.tag_context.emit_on_block_start(block_name, self._tick_number)

        # Block Time    - 0 at Block start, global but value refers to active block
        if block_name not in self.block_times.keys():
            self.block_times[block_name] = 0.0
        self.block_times[block_name] += time_increment
        self._system_tags[SystemTagName.BLOCK_TIME].set_value(self.block_times[block_name], self._tick_time)

        # Execute the tick lifetime hook on tags
        self.tag_context.emit_on_tick()

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
        try:
            for c in self.cmd_executing:
                if c not in cmds_done:
                    # Note: Executing one command may cause other commands to be cancelled (by identical or overlapping
                    # commands) Rather than modify self.cmd_executing (while iterating over it), cancelled/completed
                    # commands are added to the cmds_done set.
                    self._execute_command(c, cmds_done)
        except Exception:
            logger.error("Error executing command: {c}", exc_info=True)
            self.set_error_state()
        finally:
            for c_done in cmds_done:
                self.cmd_executing.remove(c_done)

    def _execute_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        # execute an internal engine command or a uod command

        logger.debug("Executing command: " + cmd_request.name)
        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
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
            try:
                record = self.interpreter.runtimeinfo.get_exec_record(cmd_request.exec_id)
            except ValueError:  # happens during restart
                pass

        # an existing, long running engine_command is running. other commands must wait
        command = get_running_internal_command()
        if command is not None:
            if cmd_request.name == command.name:
                if not command.is_finalized():
                    command.tick()
                if command.has_failed():
                    record.add_state_failed(self._tick_time, self._tick_number, self.tags_as_readonly())
                    cmds_done.add(cmd_request)
                elif command.is_finalized():
                    record.add_state_completed(self._tick_time, self._tick_number, self.tags_as_readonly())
                    cmds_done.add(cmd_request)
            return

        # no engine command is running - start one
        try:
            command = create_internal_command(cmd_request.name)
            if cmd_request.kvargs is not None:
                try:
                    command.init_args(cmd_request.kvargs)
                    logger.debug(f"Initialized command {cmd_request.name} with arguments {cmd_request.kvargs}")
                except Exception:
                    raise Exception(
                        f"Failed to initialize arguments '{cmd_request.kvargs}' for command '{cmd_request.name}'")
        except ValueError:
            raise NotImplementedError(f"Unknown internal engine command '{cmd_request.name}'")

        record.add_state_started(self._tick_time, self._tick_number, self.tags_as_readonly())
        command.tick()
        if command.has_failed():
            record.add_state_failed(self._tick_time, self._tick_number, self.tags_as_readonly())
            cmds_done.add(cmd_request)
        elif command.is_finalized():
            record.add_state_completed(self._tick_time, self._tick_number, self.tags_as_readonly())
            cmds_done.add(cmd_request)

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
        for name, command in self.uod.command_instances.items():
            if command.is_cancelled() or command.is_execution_complete() or command.is_finalized():
                logger.debug(f"Skipping command '{name}' that is no longer running")
            else:
                logger.debug(f"Cancelling command '{name}'")
                command.cancel()

    def _execute_uod_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        cmd_name = cmd_request.name
        assert self.uod.has_command_name(cmd_name), f"Expected Uod to have command named '{cmd_name}'"
        assert cmd_request.exec_id is not None, f"Expected uod command request '{cmd_name}' to have exec_id"

        if not self.uod.hwl.is_connected:
            raise HardwareLayerException("The hardware is not currently connected. Uod command was not allowed to start.")

        record = self.interpreter.runtimeinfo.get_exec_record(cmd_request.exec_id)

        # cancel any existing instance with same name
        for c in self.cmd_executing:
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
        for c in self.cmd_executing:
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
            if t.direction == TagDirection.OUTPUT:
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

    def notify_initial_tags(self):
        for tag in self._iter_all_tags():
            if tag.tick_time is None:
                logger.warning(f'Setting a tick time on {tag.name} tag missing it in notify_initial_tags()')
                tag.tick_time = self._tick_time
            self.tag_updates.put(tag)

    def notify_tag_updates(self):
        # pick up changes from listeners and queue them up
        for tag_name in self._system_listener.changes:
            tag = self._system_tags[tag_name]
            self.tag_updates.put(tag)
        self._system_listener.clear_changes()

        for tag_name in self._uod_listener.changes:
            tag = self.uod.tags[tag_name]
            self.tag_updates.put(tag)
        self._uod_listener.clear_changes()

    def set_error_state(self):
        logger.info("Engine Paused because of error")
        self._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.ERROR, self._tick_time)
        self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Paused, self._tick_time)
        self._runstate_paused = True

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
            hwl.write_batch(register_values, registers)
        except HardwareLayerException:
            logger.error("Hardware write_batch error", exc_info=True)
            self.stop()

    def schedule_execution(self, name: str, exec_id: UUID | None = None, **kvargs):
        """ Execute named command from interpreter """
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            request = CommandRequest.from_interpreter(name, exec_id, **kvargs)
            self.cmd_queue.put_nowait(request)
        else:
            logger.error(f"Invalid command type scheduled: {name}")
            raise ValueError(f"Invalid command type scheduled: {name}")

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
            logger.error(f"Invalid user command type scheduled: {name}")
            raise ValueError(f"Invalid user command type scheduled: {name}")

    def inject_code(self, pcode: str):
        """ Inject a general code snippet to run in the current scope of the current program. """
        # TODO return status for frontend client
        # TODO set updated method content and signal Method change
        # TODO perform this change via _method
        logger.warning("TODO set updated method content and signal Method change")
        try:
            injected_program = self.parse_pcode(pcode)
            self.interpreter.inject_node(injected_program)
            logger.info("Injected code successful")
        except Exception as ex:
            logger.info("Injected code parse error: " + str(ex))
            self.set_error_state()
            # TODO: possibly raise ...

    # code manipulation api
    def set_method(self, method: Mdl.Method):
        """ Set new method. This will replace the current method and invoke the on_method_init callback. """
        try:
            self._method.set_method(method)
            logger.info(f"New method set with {len(method.lines)} lines")
        except Exception:
            logger.error("Failed to set method", exc_info=True)
            self.set_error_state()
            # TODO: possibly raise ...

    def calculate_method_state(self) -> Mdl.MethodState:
        return self._method.calculate_method_state(self.interpreter.runtimeinfo)
