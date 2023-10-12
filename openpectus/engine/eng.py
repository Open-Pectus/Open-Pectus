from __future__ import annotations
from enum import StrEnum
import itertools
from multiprocessing import Queue
from queue import Empty
import logging
import time
from typing import Iterable, List, Set

from openpectus.lang.exec.commands import CommandRequest
from openpectus.lang.exec.pinterpreter import InterpreterContext, PInterpreter
from openpectus.lang.exec.runlog import RunLog, RunLogItemState
from openpectus.lang.exec.timer import EngineTimer, OneThreadTimer
from openpectus.engine.hardware import HardwareLayerBase, HardwareLayerException
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.lang.exec.tags import (
    DEFAULT_TAG_SYSTEM_STATE,
    DEFAULT_TAG_METHOD_STATUS,
    Tag,
    TagCollection,
    TagDirection,
    TagValue,
    TagValueCollection,
    ChangeListener,
    DEFAULT_TAG_CLOCK,
    DEFAULT_TAG_RUN_COUNTER,
)
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram

logger = logging.getLogger("Engine")


def parse_pcode(pcode: str) -> PProgram:
    p = PGrammar()
    p.parse(pcode)
    return p.build_model()


class ExecutionEngine():
    """ Main engine class. Handles
    - io loop, reads and writes hardware process image (sync)
    - invokes interpreter to interpret next instruction (sync, generator based)
    - signals state changes via tag_updates queue (to aggregator via websockets, natively async)
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

        # TODO does the uod need to know about these? Yes - we should make them available as read only
        self._system_tags = TagCollection.create_system_tags()

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

        self._interpreter: PInterpreter = PInterpreter(PProgram(), EngineInterpreterContext(self))
        """ The interpreter executing the current program. """

    def _iter_all_tags(self) -> Iterable[Tag]:
        return itertools.chain(self._system_tags, self.uod.tags)

    def tags_as_readonly(self) -> TagValueCollection:
        return TagValueCollection(t.as_readonly() for t in self._iter_all_tags())

    def cleanup(self):
        self.cmd_queue.cancel_join_thread()
        self.tag_updates.cancel_join_thread()

    @property
    def interpreter(self) -> PInterpreter:
        if self._interpreter is None:
            raise ValueError("No interpreter set")
        return self._interpreter

    @property
    def runlog(self) -> RunLog:
        return self.interpreter.runlog

    @property
    def _tag_names_dirty(self) -> list[str]:
        dirty = set()
        for tag_name in self._system_listener.changes:
            dirty.add(tag_name)
        for tag_name in self._uod_listener.changes:
            dirty.add(tag_name)
        return list(dirty)

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

    def tick(self):
        """ Performs a scan cycle tick. """
        logger.debug(f"Tick {self._tick_number + 1}")

        if not self._running:
            self._tick_timer.stop()
            # TODO shutdown

        self._tick_time = time.time()
        self._tick_number += 1

        # sys_tags = self.system_tags.clone()  # TODO clone does not currently support the subclasses
        # uod_tags = self.uod.tags.clone()

        # read
        self.read_process_image()

        # update calculated tags
        # TODO

        # excecute interpreter tick
        self._interpreter.tick(self._tick_time, self._tick_number)

        # update clocks
        self.update_tags()

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

        hwl: HardwareLayerBase = self.uod.hwl

        # assert isinstance(self.uod.hwl, HardwareLayerBase) is True
        if not isinstance(hwl, HardwareLayerBase):
            logger.error("Hmm")  # TODO this is really weird. figure out why this happens

        registers = hwl.registers
        register_values = hwl.read_batch(list(registers.values()))
        for i, r in enumerate(registers.values()):
            tag = self.uod.tags.get(r.name)
            tag_value = register_values[i]
            if "to_tag" in r.options:
                tag_value = r.options["to_tag"](tag_value)
            tag.set_value(tag_value)

    def update_tags(self):
        # TODO figure out engine/interpreter work split on clock tags
        # it appears that interpreter will have to update scope times
        # - unless we allow scope information to pass to engine (which we might)

        clock = self._system_tags.get(DEFAULT_TAG_CLOCK)
        clock.set_value(time.time())

    def execute_commands(self):
        done = False
        # add command request from incoming queue

        # TODO decide whether to parse or not
        # program = parse_pcode("")
        # instructions = program.get_instructions(include_blanks=False)
        # if len(instructions) == 1 and isinstance(instructions[0], PCommand)

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
                    self._system_tags[DEFAULT_TAG_METHOD_STATUS].set_value(MethodStatusEnum.ERROR)
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

        if EngineCommandEnum.has_value(cmd_request.name):
            self._execute_internal_command(cmd_request, cmds_done)
        else:
            self._execute_uod_command(cmd_request, cmds_done)

    def _execute_internal_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):

        if not self._runstate_started and cmd_request.name != EngineCommandEnum.START:
            logger.warning(f"Command {cmd_request.name} is invalid when Engine is not running")
            return

        match cmd_request.name:
            case EngineCommandEnum.START:
                if self._runstate_started:
                    logger.warning("Cannot start when already running")
                    return
                self._runstate_started = True
                self._runstate_started_time = time.time()
                self._runstate_paused = False
                self._runstate_holding = False
                self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Running)
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case EngineCommandEnum.STOP:
                self._runstate_started = False
                self._runstate_paused = False
                self._runstate_holding = False
                self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Stopped)
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case EngineCommandEnum.PAUSE:
                self._runstate_paused = True
                self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Paused)
                self._apply_safe_state()
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case EngineCommandEnum.UNPAUSE:
                self._runstate_paused = False
                if self._runstate_holding:
                    self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Holding)
                else:
                    self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Running)
                self._apply_safe_state()
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case EngineCommandEnum.HOLD:
                self._runstate_holding = True
                if not self._runstate_paused:
                    self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Holding)
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case EngineCommandEnum.UNHOLD:
                self._runstate_holding = False
                if not self._runstate_paused:
                    self._system_tags[DEFAULT_TAG_SYSTEM_STATE].set_value(SystemStateEnum.Running)
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case EngineCommandEnum.INCREMENT_RUN_COUNTER:
                value = self._system_tags[DEFAULT_TAG_RUN_COUNTER].as_number() + 1
                self._system_tags[DEFAULT_TAG_RUN_COUNTER].set_value(value)
                cmds_done.add(cmd_request)
                self.runlog.add_completed(cmd_request, self._tick_time, self._tick_number, self.tags_as_readonly())

            case _:
                raise NotImplementedError(f"Internal engine command '{cmd_request.name}' execution not implemented")

    def _execute_uod_command(self, cmd_request: CommandRequest, cmds_done: Set[CommandRequest]):
        cmd_name = cmd_request.name
        assert self.uod.has_command_name(cmd_name), f"Expected Uod to have command named {cmd_name}"

        # cancel any existing instance with same name
        for c in self.cmd_executing:
            if c.name == cmd_name and not c == cmd_request:
                cmds_done.add(c)
                c_item = self.runlog.get_item_by_cmd(c)
                assert c_item is not None
                if c_item.command is not None:
                    c_item.command.cancel()
                c_item.add_end_state(
                    RunLogItemState.Cancelled,
                    self._tick_time,
                    self._tick_number,
                    self.tags_as_readonly())
                logger.debug(f"Running command {c.name} cancelled because another was started")

        # cancel any overlapping instance
        for c in self.cmd_executing:
            if not c == cmd_request:
                for overlap_list in self.uod.overlapping_command_names_lists:
                    if c.name in overlap_list and cmd_name in overlap_list:
                        cmds_done.add(c)
                        c_item = self.runlog.get_item_by_cmd(c)
                        assert c_item is not None
                        if c_item.command is not None:
                            c_item.command.cancel()
                        c_item.add_end_state(
                            RunLogItemState.Cancelled,
                            self._tick_time,
                            self._tick_number,
                            self.tags_as_readonly())
                        logger.debug(
                            f"Running command {c.name} cancelled because overlapping command " +
                            f"'{cmd_name}' was started")
                        break

        # create or get command instance
        if not self.uod.has_command_instance(cmd_name):
            uod_command = self.uod.create_command(cmd_name)
            runlog_item = self.runlog.add_waiting(cmd_request, uod_command, self._tick_time, self._tick_number)
        else:
            uod_command = self.uod.get_command(cmd_name)
            runlog_item = self.runlog.get_item_by_cmd(cmd_request)

        assert uod_command is not None
        assert runlog_item is not None

        args = uod_command.parse_args(cmd_request.args, uod_command.context)  # TODO remove uod from method signature
        if args is None:
            logger.error(f"Invalid argument string: '{cmd_request.args}' for command '{cmd_name}'")
            raise ValueError("Invalid arguments")

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
                runlog_item.add_start_state(self._tick_time, self._tick_number, self.tags_as_readonly())
                uod_command.execute(args)
                logger.debug(f"Command {cmd_request.name} executed first iteration {uod_command._exec_iterations}")
            elif not uod_command.is_execution_complete():
                uod_command.execute(args)
                logger.debug(f"Command {cmd_request.name} executed another iteration {uod_command._exec_iterations}")

            if uod_command.is_execution_complete() and not uod_command.is_finalized():
                runlog_item.add_end_state(
                    RunLogItemState.Completed,
                    self._tick_time,
                    self._tick_number,
                    self.tags_as_readonly())
                cmds_done.add(cmd_request)
                uod_command.finalize()
                logger.debug(f"Command {cmd_request.name} finalized")

        except Exception as ex:
            if cmd_request in self.cmd_executing:
                cmds_done.add(cmd_request)
            item = self.runlog.get_item_by_cmd(cmd_request)
            if item is not None:
                item.add_end_state(
                    RunLogItemState.Failed,
                    self._tick_time,
                    self._tick_number,
                    self.tags_as_readonly())
                if item.command is not None and not item.command.is_cancelled:
                    item.command.cancel()

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
                    t.set_value(safe_value)

        return TagValueCollection(current_values)

    def _apply_state(self, state: TagValueCollection):
        for t in self._iter_all_tags():
            if state.has(t.name):
                tag_value = state.get(t.name)
                t.set_value(tag_value.value)

    def notify_initial_tags(self):
        for tag in self._iter_all_tags():
            self.tag_updates.put(tag)

    def notify_tag_updates(self):
        for tag_name in self._system_listener.changes:
            tag = self._system_tags[tag_name]
            self.tag_updates.put(tag)
        self._system_listener.clear_changes()

        for tag_name in self._uod_listener.changes:
            tag = self.uod.tags[tag_name]
            self.tag_updates.put(tag)
        self._uod_listener.clear_changes()

    def write_process_image(self):
        hwl: HardwareLayerBase = self.uod.hwl

        register_values = []
        register_list = list(hwl.registers.values())
        for r in register_list:
            tag_value = self.uod.tags[r.name].get_value()
            register_value = tag_value
            if "from_tag" in r.options:
                register_value = r.options["from_tag"](tag_value)
            register_values.append(register_value)

        hwl.write_batch(register_values, register_list)

    # differentiate between injected commands (which are to be executed asap without modifying the program)
    # and non-injected which are either
    # - already part of the program
    # - uod commands that engine cant just execute (if they have no threshold)

    def schedule_execution(self, name: str, args: str | None = None) -> CommandRequest:
        """ Execute named command (engine internal or Uod), possibly with arguments. """
        if EngineCommandEnum.has_value(name) or self.uod.has_command_name(name):
            request = CommandRequest(name, args)
            self.cmd_queue.put_nowait(request)
            return request
        else:
            raise ValueError("Invalid command type scheduled")

    def inject_command(self, name: str, args: str):
        """ Inject a command to run in the current scope of the current program. """
        # Helper for inject_code()
        raise NotImplementedError()

    def inject_code(self, pcode: str):
        """ Inject a general code snippet to run in the current scope of the current program. """
        # TODO return status for frontend client
        try:
            injected_program = parse_pcode(pcode)
            self.interpreter.inject_node(injected_program)
        except Exception as ex:
            logger.info("Injected code parse error: " + str(ex))

    # code manipulation api
    def set_program(self, pcode: str):
        """ Set new program. This will replace the current program. """

        if self._interpreter is not None:
            self._interpreter.stop()
            # TODO possible clean up more stuff
            logger.info("Interpreter stopped")

        try:
            program = parse_pcode(pcode=pcode)
            self._interpreter = PInterpreter(program, EngineInterpreterContext(self))
        except Exception:
            logger.error("Failed to set code", exc_info=True)
            raise ValueError()

    def set_pprogram(self, program: PProgram):
        """ Set new program. This will replace the current program. """

        if self._interpreter is not None:
            self._interpreter.stop()
            # TODO possible clean up more stuff
            logger.info("Interpreter stopped")

        self._interpreter = PInterpreter(program, EngineInterpreterContext(self))

    # set_code, update_line
    # undo/revert(?)


class EngineInterpreterContext(InterpreterContext):
    def __init__(self, engine: ExecutionEngine) -> None:
        super().__init__()

        self.engine = engine
        self._tags = engine.uod.system_tags.merge_with(engine.uod.tags)

    @property
    def tags(self) -> TagCollection:
        return self._tags

    def schedule_execution(self, name: str, args: str | None = None) -> CommandRequest:
        return self.engine.schedule_execution(name, args)


class EngineCommandEnum(StrEnum):
    START = "Start"
    STOP = "Stop"
    PAUSE = "Pause"
    UNPAUSE = "Unpause"
    HOLD = "Hold"
    UNHOLD = "Unhold"
    INCREMENT_RUN_COUNTER = "Increment run counter"

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return value in EngineCommandEnum.__members__.values()


class SystemStateEnum(StrEnum):
    Running = "Running",
    Paused = "Paused",
    Holding = "Holding",
    Waiting = "Waiting",
    Stopped = "Stopped"


class MethodStatusEnum(StrEnum):
    OK = "OK",
    ERROR = "Error"
