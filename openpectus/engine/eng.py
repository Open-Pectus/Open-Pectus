from __future__ import annotations
from enum import StrEnum, auto
import itertools
from multiprocessing import Queue
from queue import Empty
import logging
import time
from typing import Iterable

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


logging.basicConfig()
logger = logging.getLogger("Engine")
logger.setLevel(logging.DEBUG)


class UodReader():
    def read(self) -> UnitOperationDefinitionBase:
        raise NotImplementedError()


class EngineCommand():
    """ Represents a command request for engine to execute. """
    def __init__(self, name: str, args: str | None = None) -> None:
        self.name: str = name
        self.args: str | None = args


class EngineInternalCommand(StrEnum):
    START = auto()
    STOP = auto()
    PAUSE = auto()
    HOLD = auto()

    @staticmethod
    def has_value(value: str):
        """ Determine if enum has this string value defined. Case sensitive. """
        return hasattr(EngineInternalCommand, value)


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

        self.cmd_queue: Queue[EngineCommand] = Queue()
        """ Commands to execute, coming from interpreter and from aggregator """
        self.tag_updates: Queue[Tag] = Queue()
        """ Tags updated in last tick """

        self._uod_listener = ChangeListener()
        self._system_listener = ChangeListener()
        self._tick_timer = OneThreadTimer(tick_interval, self.tick)

        self._runstate_started: bool = False
        """ Indicates the surrent Start/Stop state"""
        self._runstate_started_time: float = 0

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
        # configure uod
        self.uod.define_system_tags(self._system_tags)
        self.uod.define()
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
        # TODO

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

        hwl: HardwareLayerBase = self.uod.hwl  # type: ignore

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
        while self.cmd_queue.qsize() > 0 and not done:
            try:
                c = self.cmd_queue.get()
                self._execute_command(c)
            except Empty:
                done = True

    def _execute_command(self, cmd_request: EngineCommand):
        logger.debug("Executing command request: " + cmd_request.name)
        if cmd_request.name is None or len(cmd_request.name.strip()) == 0:
            logger.error("Command name empty")
            raise ValueError("Command name empty")

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
            elif cmd_name == EngineInternalCommand.STOP.upper():
                self._runstate_started = False
            else:
                raise NotImplementedError()
        else:
            if not self.uod.validate_command_name(cmd_request.name):
                # TODO handle internal commands also
                logger.error("No such uod command")
                raise ValueError("No such command")

            if not self.uod.validate_command_args(cmd_request.name, cmd_request.args):
                logger.error(f"Invalid argument string: '{cmd_request.args}' for command '{cmd_request.name}'")
                raise ValueError("Invalid arguments")

            try:
                logger.debug(f"Executing uod command: '{cmd_request.name}' with args '{cmd_request.args}'")
                self.uod.execute_command(cmd_request.name, cmd_request.args)
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
        hwl: HardwareLayerBase = self.uod.hwl  # type: ignore

        register_values = []
        register_list = list(hwl.registers.values())
        for r in register_list:
            tag_value = self.uod.tags[r.name].get_value()
            register_value = tag_value
            if "from_tag" in r.options:
                register_value = r.options["from_tag"](tag_value)
            register_values.append(register_value)

        hwl.write_batch(register_values, register_list)

    def schedule_execution(self, name: str, args: str) -> None:
        command = EngineCommand(name, args)
        self.cmd_queue.put_nowait(command)

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
