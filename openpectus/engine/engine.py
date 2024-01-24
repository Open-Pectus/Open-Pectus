import itertools
import logging
import time
import uuid
from queue import Empty, Queue
from typing import Iterable, List, Set
from uuid import UUID

from openpectus.engine.hardware import HardwareLayerBase, HardwareLayerException
from openpectus.engine.method_model import MethodModel
from openpectus.engine.models import MethodStatusEnum, SystemStateEnum, EngineCommandEnum
from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.errors import InterpretationError
from openpectus.lang.exec.pinterpreter import PInterpreter, InterpreterContext
from openpectus.lang.exec.runlog import RuntimeInfo, RunLog
from openpectus.lang.exec.tags import (
    Tag,
    TagCollection,
    TagDirection,
    TagValue,
    TagValueCollection,
    ChangeListener,
    SystemTagName,
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

    def cleanup(self):
        pass

    @property
    def interpreter(self) -> PInterpreter:
        if self._interpreter is None:
            raise ValueError("No interpreter set")
        return self._interpreter

    @property
    def runtimeinfo(self) -> RuntimeInfo:
        return self.interpreter.runtimeinfo

    def get_runlog(self) -> RunLog:
        return self.runtimeinfo.get_runlog()

    def _configure(self):
        self.uod.validate_configuration()
        self.uod.tags.add_listener(self._uod_listener)
        self._system_tags.add_listener(self._system_listener)

    def run(self):
        self._configure()
        self._run()

    def is_running(self) -> bool:
        return self._running

    def _run(self):
        """ Starts the scan cycle """

        assert self.uod is not None
        assert self.uod.hwl is not None

        try:
            self.uod.hwl.connect()
            logger.info("Hardware connected")
        except HardwareLayerException:
            logger.error("Hardware connect error", exc_info=True)
            return  # TODO retry/reconnect

        self._running = True
        self._tick_timer.start()

    def stop(self):
        self.uod.hwl.disconnect()
        self._running = False
        self._tick_timer.stop()
        self.cleanup()

    def tick(self):
        """ Performs a scan cycle tick. """
        logger.debug(f"Tick {self._tick_number + 1}")

        if not self._running:
            self._tick_timer.stop()
            # TODO shutdown

        self._tick_time = time.time()
        self._tick_number += 1

        # Perform certain things in first tick
        if self._tick_number == 0:
            # System tags are initialized before first tick, without a tick time, and some are never updated, so
            # provide first tick time as a "default".
            for tag in self._system_tags.tags.values():
                tag.tick_time = self._tick_time

        # sys_tags = self.system_tags.clone()  # TODO clone does not currently support the subclasses
        # uod_tags = self.uod.tags.clone()

        # read
        self.read_process_image()

        # excecute interpreter tick
        if self._runstate_started and not self._runstate_paused and not self._runstate_holding:
            try:
                self._interpreter.tick(self._tick_time, self._tick_number)
            except InterpretationError:
                logger.error("Interpretation error", exc_info=True)
                self.set_error_state()
            except Exception:
                logger.error("Unhandled interpretation error", exc_info=True)
                self.set_error_state()

        # update calculated tags
        self.update_calculated_tags()

        # execute queued commands
        self.execute_commands()

        # notify of tag changes
        self.notify_tag_updates()

        # write
        self.write_process_image()

    def read_process_image(self):
        """ Read data from relevant hw registers into tags"""

        # call poi.read(requested_tags)
        # this does in OPCUA:
        #   get the 'path' from uod: tag_io = self.map.get(tag.name, None)
        #   if available, collects tag, path, and fn
        #       io_tags.append(tag)
        #       pio_tags.append(tag_io['path'])
        #       fns.append(tag_io.get('fn', lambda x: x))
        #   performs batch read of raw io values:
        #       values = self._read(pio_tags)
        #   writes values to tags using the conversion fn defined in uod (or x->x if no fn defined):
        #       if values:
        #           [tag.write(fn(value)) for tag, fn, value in zip(io_tags, fns, values)]

        # only do this for input tags:
        #   if tag.direction is Direction.INPUT

        # readable_tags = [t for t in self._iter_all_tags() if t.direction == TagDirection.INPUT]
        # values = self.uod.hwl.read_batch(readable_tags)
        # for tag, value in zip(readable_tags, values):
        #     tag.set_value(value)

        registers = self.uod.hwl.registers
        register_values = self.uod.hwl.read_batch(list(registers.values()))
        for i, r in enumerate(registers.values()):
            tag = self.uod.tags.get(r.name)
            tag_value = register_values[i]
            if "to_tag" in r.options:
                tag_value = r.options["to_tag"](tag_value)
            tag.set_value(tag_value, self._tick_time)

    def update_calculated_tags(self):
        # TODO: update calculated tags

        # TODO figure out engine/interpreter work split on clock tags
        # it appears that interpreter will have to update scope times
        # - unless we allow scope information to pass to engine (which we might)
        clock = self._system_tags.get(SystemTagName.CLOCK)
        clock.set_value(time.time(), self._tick_time)

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
        for c in self.cmd_executing:
            if c not in cmds_done:
                try:
                    # Note: Executing one command may cause other commands to be cancelled (by identical or overlapping
                    # commands) Rather than modify self.cmd_executing (while iterating over it), cancelled/completed
                    # commands are added to the cmds_done set.
                    self._execute_command(c, cmds_done)
                except Exception:
                    logger.error("Error executing command: {c}", exc_info=True)
                    self._system_tags[SystemTagName.METHOD_STATUS].set_value(MethodStatusEnum.ERROR, self._tick_time)
                    # TODO stop or pause or something
                    break
        for c_done in cmds_done:
            self.cmd_executing.remove(c_done)

    def _execute_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        # execute an internal engine command or a uod command

        logger.debug("Executing command: " + cmd_request.name)
        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
            cmds_done.add(cmd_request)
            return

        try:
            if EngineCommandEnum.has_value(cmd_request.name):
                self._execute_internal_command(cmd_request, cmds_done)
            else:
                self._execute_uod_command(cmd_request, cmds_done)
        except Exception as ex:
            logger.error(f"Error running command {cmd_request.name}", str(ex))
            self.set_error_state()

    def _execute_internal_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):

        if not self._runstate_started and cmd_request.name != EngineCommandEnum.START:
            logger.warning(f"Command {cmd_request.name} is invalid when Engine is not running")
            cmds_done.add(cmd_request)
            return

        def record_state_add_started_and_completed():
            if cmd_request.exec_id is None:
                # has been seen to fail for Stop - more runtime data needed to decide
                logger.error(f"Expected exec_id set for command {cmd_request.name}")
            else:
                record = self.interpreter.runtimeinfo.get_exec_record(cmd_request.exec_id)
                record.add_state_started(self._tick_time, self._tick_number, self.tags_as_readonly())
                record.add_state_completed(self._tick_time, self._tick_number, self.tags_as_readonly())

        match cmd_request.name:
            case EngineCommandEnum.START:
                if self._runstate_started:
                    logger.warning("Cannot start when already running")
                    cmds_done.add(cmd_request)
                    return
                self._runstate_started = True
                self._runstate_started_time = time.time()
                self._runstate_paused = False
                self._runstate_holding = False
                self._system_tags[SystemTagName.RUN_ID].set_value(str(uuid.uuid4()), self._tick_time)
                self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, self._tick_time)
                cmds_done.add(cmd_request)
                # Note: can't add record for Start command, because exec_id has not been set until Start has run

            case EngineCommandEnum.STOP:
                self._runstate_started = False
                self._runstate_paused = False
                self._runstate_holding = False
                self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Stopped, self._tick_time)
                self._system_tags[SystemTagName.RUN_ID].set_value(None, self._tick_time)
                self.interpreter.stop()
                self._interpreter = PInterpreter(self._method.get_program(), self)
                cmds_done.add(cmd_request)
                record_state_add_started_and_completed()

            case EngineCommandEnum.PAUSE:
                self._runstate_paused = True
                self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Paused, self._tick_time)
                self._apply_safe_state()
                cmds_done.add(cmd_request)
                record_state_add_started_and_completed()

            case EngineCommandEnum.UNPAUSE:
                self._runstate_paused = False
                if self._runstate_holding:
                    self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Holding, self._tick_time)
                else:
                    self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, self._tick_time)
                self._apply_safe_state()
                cmds_done.add(cmd_request)
                record_state_add_started_and_completed()

            case EngineCommandEnum.HOLD:
                self._runstate_holding = True
                if not self._runstate_paused:
                    self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Holding, self._tick_time)
                cmds_done.add(cmd_request)
                record_state_add_started_and_completed()

            case EngineCommandEnum.UNHOLD:
                self._runstate_holding = False
                if not self._runstate_paused:
                    self._system_tags[SystemTagName.SYSTEM_STATE].set_value(SystemStateEnum.Running, self._tick_time)
                cmds_done.add(cmd_request)
                record_state_add_started_and_completed()

            case EngineCommandEnum.INCREMENT_RUN_COUNTER:
                value = self._system_tags[SystemTagName.RUN_COUNTER].as_number() + 1
                self._system_tags[SystemTagName.RUN_COUNTER].set_value(value, self._tick_time)
                cmds_done.add(cmd_request)
                record_state_add_started_and_completed()

            case _:
                raise NotImplementedError(f"Internal engine command '{cmd_request.name}' execution not implemented")

    def _execute_uod_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        cmd_name = cmd_request.name
        assert self.uod.has_command_name(cmd_name), f"Expected Uod to have command named '{cmd_name}'"
        assert cmd_request.exec_id is not None, f"Expected uod command request '{cmd_name}' to have exec_id"

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

        args = uod_command.parse_args(cmd_request.args, uod_command.context)  # TODO remove uod from method signature
        if args is None:
            logger.error(f"Invalid argument string: '{cmd_request.args}' for command '{cmd_name}'")
            raise ValueError(f"Invalid arguments for command '{cmd_name}'")

        # execute command state flow
        try:
            logger.debug(
                f"Executing uod command: '{cmd_request.name}' with args '{cmd_request.args}', " +
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
                uod_command.execute(args)
                logger.debug(f"Command {cmd_request.name} executed first iteration {uod_command._exec_iterations}")
            elif not uod_command.is_execution_complete():
                uod_command.execute(args)
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
                if command is not None and not command.is_cancelled:
                    command.cancel()
                    logger.info(f"Cleaned up failed command {cmd_name}")

            logger.error(
                f"Uod command execution failed. Command: '{cmd_request.name}', " +
                f"argument string: '{cmd_request.args}'", exc_info=True)
            raise ex

    def _apply_safe_state(self) -> TagValueCollection:
        current_values: List[TagValue] = []

        for t in self._iter_all_tags():
            if t.direction == TagDirection.OUTPUT:
                # TODO safe value can actually be None so we'll need
                # additional data to determine whether a safe value is present
                safe_value = t.safe_value
                if safe_value is not None:
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
        logger.info("Paused because of error")
        self._runstate_paused = True

    #TODO remove
    def parse_pcode(self, pcode: str) -> PProgram:
        p = PGrammar()
        p.parse(pcode)
        return p.build_model()

    def write_process_image(self):
        hwl: HardwareLayerBase = self.uod.hwl

        register_values = []
        register_list = list(hwl.registers.values())
        for r in register_list:
            tag_value = self.uod.tags[r.name].get_value()
            register_value = tag_value if "from_tag" not in r.options \
                else r.options["from_tag"](tag_value)
            register_values.append(register_value)

        hwl.write_batch(register_values, register_list)

    # differentiate between injected commands (which are to be executed asap without modifying the program)
    # and non-injected which are either
    # - already part of the program
    # - uod commands that engine cant just execute (if they have no threshold)

    @property
    def tags(self) -> TagCollection:
        return self._system_tags.merge_with(self.uod.tags)

    def schedule_execution(self, name: str, args: str | None = None, exec_id: UUID | None = None):
        """ Execute named command (engine internal or Uod), possibly with arguments. """
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            request = CommandRequest(name, args, exec_id)
            self.cmd_queue.put_nowait(request)
        else:
            logger.error(f"Invalid command type scheduled: {name}")
            self.set_error_state()

    def inject_command(self, name: str, args: str):
        """ Inject a command to run in the current scope of the current program. """
        # Helper for inject_code()
        raise NotImplementedError()

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

    # code manipulation api
    def set_method(self, method: Mdl.Method):
        """ Set new method. This will replace the current method and invoke the on_method_init callback. """
        try:
            self._method.set_method(method)
            logger.info(f"New method set with {len(method.lines)} lines")
        except Exception:
            logger.error("Failed to set method", exc_info=True)
            self.set_error_state()

    def calculate_method_state(self) -> Mdl.MethodState:
        return self._method.calculate_method_state(self.interpreter.runtimeinfo)
