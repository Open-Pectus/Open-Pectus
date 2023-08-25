from __future__ import annotations
from enum import StrEnum, auto
import itertools
from multiprocessing import Queue
from queue import Empty
import logging
import time
from typing import Iterable, List
from openpectus.lang.exec.pinterpreter import PInterpreter

from openpectus.lang.exec.timer import OneThreadTimer
from openpectus.engine.hardware import HardwareLayerBase, HardwareLayerException
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.lang.exec.tags import (
    DEFAULT_TAG_RUN_TIME,
    Tag,
    TagCollection,
    ChangeListener,
    DEFAULT_TAG_CLOCK
)
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram


logging.basicConfig()
logger = logging.getLogger("Engine")
logger.setLevel(logging.DEBUG)


def parse_pcode(pcode: str) -> PProgram:
    p = PGrammar()
    p.parse(pcode)
    return p.build_model()


class UodReader():
    def read(self) -> UnitOperationDefinitionBase:
        raise NotImplementedError()


class CommandRequest():
    # TODO extend to support general pcode and injection flag?
    """ Represents a command request for engine to execute. """
    def __init__(self, name: str, args: str | None = None) -> None:
        self.name: str = name
        self.args: str | None = args

    def __str__(self) -> str:
        return f"EngineCommand {self.name} | args: {self.args}"


class EngineInternalCommand(StrEnum):
    START = auto()
    STOP = auto()
    PAUSE = auto()
    HOLD = auto()

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return hasattr(EngineInternalCommand, value)


class RunLogItem():
    def __init__(self) -> None:
        pass
        # self.command =

# TODO be able to create interpreter
# TODO advance interpreter - it should no longe have its own timer


class ExecutionEngine():
    """ Main engine class. Handles
    - io loop, reads and writes hardware process image (sync)
    - invokes interpreter if a program is loaded (sync, generator based)
    - signals state changes via tag_updates queue (to aggregator via websockets, natively async)
    - accepts commands from cmd_queue (from interpreter and from aggregator)
    """
    def __init__(self, uod: UnitOperationDefinitionBase, tick_interval=0.1) -> None:
        self.uod = uod
        self._running: bool = False
        """ Indicates whether the scan cycle loop is running, set to False to shut down"""

        self._tick_time: float = 0.0
        """ The time of the last tick """

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
        self._tick_timer = OneThreadTimer(tick_interval, self.tick)

        self._runstate_started: bool = False
        """ Indicates the current Start/Stop state"""
        self._runstate_started_time: float = 0

        self._interpreter: PInterpreter | None = None
        """ The interpreter executing the current program, if any. """

    def _iter_all_tags(self) -> Iterable[Tag]:
        return itertools.chain(self._system_tags, self.uod.tags)

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
        logger.debug("tick")

        if not self._running:
            self._tick_timer.stop()
            # TODO shutdown

        self._tick_time = time.time()

        # sys_tags = self.system_tags.clone()  # TODO clone does not currently support the subclasses
        # uod_tags = self.uod.tags.clone()

        # read
        self.read_process_image()

        # update calculated tags
        # TODO

        # excecute interpreter tick
        if self._interpreter is not None:
            self._interpreter.tick(self._tick_time)

        # update clocks
        self.update_clocks()

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

    def update_clocks(self):
        if self._runstate_started:
            clock = self._system_tags.get(DEFAULT_TAG_CLOCK)
            clock.set_value(self._tick_time)
            run_time = self._system_tags.get(DEFAULT_TAG_RUN_TIME)
            run_time.set_value(self._tick_time - self._runstate_started_time)

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
                self.cmd_executing.insert(0, engine_command)
            except Empty:
                done = True

        # execute a tick of each running command
        for c in self.cmd_executing:
            try:
                self._execute_command(c)
            except Exception:
                logger.error("Error executing command: {c}", exc_info=True)
                # TODO stop or pause or something
                break

    def _execute_command(self, cmd_request: CommandRequest):
        # TODO decide whether to parse or not
        # TODO create state diagram of command execution/iterations/cancellation
        # TODO add command to force condition and add interpreter api for it
        # TODO add helper methods on PProgram to determine simple commands

        logger.debug("Executing uod command: " + cmd_request.name)
        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
            return

        # Command types
        # 1. Engine internal, i.e. START
        # 2. Uod, ie. RESET
        # 3. Interpreter, i.e. MARK

        # TODO - how do we execute a type 3. ?
        # TODO consider command types and callers:
        # caller==interpreter -> should only call with engine and uod commands
        # caller==frontend -> command could be anything

        cmd_name = cmd_request.name.upper()
        if EngineInternalCommand.has_value(cmd_name):
            if cmd_name == EngineInternalCommand.START.upper():
                self._runstate_started = True
                self._runstate_started_time = time.time()
                self.cmd_executing.remove(cmd_request)
            elif cmd_name == EngineInternalCommand.STOP.upper():
                self._runstate_started = False
                self.cmd_executing.remove(cmd_request)
            else:
                raise NotImplementedError(f"EngineInternalCommand {cmd_name} execution not implemented")
        elif False:
            # TODO internal commands
            pass
        else:
            assert self.uod.has_command_name(cmd_request.name), f"Expected Uod to have command named {cmd_request.name}"

            uod_command = self.uod.get_or_create_command(cmd_request.name)
            assert uod_command is not None, "Should always be able to get or create command"

            args = uod_command.parse_args(cmd_request.args, uod_command.context)  # TODO remove uod from method signature
            if args is None:
                logger.error(f"Invalid argument string: '{cmd_request.args}' for command '{cmd_request.name}'")
                raise ValueError("Invalid arguments")

            try:
                # cancel any existing instance
                for c in self.cmd_executing:
                    if c.name == cmd_request.name and not c == cmd_request:
                        self.cmd_executing.remove(c)
                        uod_command.cancel()
                        # TODO mark cancelled in run log

                # cancel any overlapping instance
                # TODO

                try:
                    logger.debug(f"Executing uod command: '{cmd_request.name}' with args '{cmd_request.args}'")
                    if uod_command.is_cancelled():
                        if not uod_command.is_finalized():
                            uod_command.finalize()
                        #handle cancelled

                    if not uod_command.is_initialized():
                        uod_command.initialize()

                    if not uod_command.is_execution_started():
                        uod_command.execute(args)

                    if uod_command.is_execution_complete() and not uod_command.is_finalized():
                        uod_command.finalize()

                except Exception:
                    logger.error(f"Command execution failed. Command: '{cmd_request.name}', "
                                 + "argument string: '{cmd_request.args}'", exc_info=True)
                    return

                # TODO decide responsibilities:
                # Engine:
                #   invoke initialize, execute, finalize, cancel on Uod
                #      only execute is non-synchronous
                #   update iterations after each execute call
                # Uod:
                #   set progress, set complete

            except Exception:
                logger.error("Command execution failed", exc_info=True)

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
    # and non-injected which are already part of the program

    def schedule_execution(self, name: str, args: str) -> None:
        """ Schedule execution of named command, possibly with arguments"""
        # TODO might want to check that no threshold is provided. this is not supported here
        command = CommandRequest(name, args)
        self.cmd_queue.put_nowait(command)

    def inject_command(self, name: str, args: str):
        """ Inject a command to run in the current scope of the current program. """
        # TODO might want to check that no threshold is provided. this is not supported here
        raise NotImplementedError()

    def inject_snippet(self, pcode: str):
        """ Inject a general code snippet to run in the current scope of the current program. """
        raise NotImplementedError()

    # code manipulation api
    def set_program(self, pcode: str):
        """ Set new program. This will replace the current program. """
        raise NotImplementedError()

    # set_code, update_line
    # undo/revert(?)


# Tag.Select (self.hw_value = self.read)
# Tag state     'Reset'   'N/A'
# io value
# pio value     1       0

# Tag.ValveNC (hw_value: return 0 if r == self.safe_state else return 1)
# Tag state     'Closed'    'Open'
# io value
# pio value     0           1

# Tag.Text (hw_value=read)

# Tag.Output (self.hw_value=self.float)
