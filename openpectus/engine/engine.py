
import itertools
from multiprocessing import Queue
from queue import Empty
import time
from typing import Iterable
from lang.exec.uod import UnitOperationDefinitionBase
from lang.exec.tags import Tag, TagDirection, TagCollection
import logging

from engine.hardware import HardwareLayerException
from engine.hardware import HardwareLayerBase
from lang.exec.tags import ChangeListener


logging.basicConfig()
logger = logging.getLogger("Engine")
logger.setLevel(logging.DEBUG)


class UodReader():
    def read(self) -> UnitOperationDefinitionBase:
        raise NotImplementedError()


# Engine-interpreter interface?
#  built-in commands vs uod commands? do they need separate definitions. 
#   The builtins don't really need any - not for the interpreter - but for the UI they do
#   Change interpreter - is should not directly execute uod commands - should hand them to engine for execution

class InterpreterEngine():
    def queue_command(self, cmd_name, cmd_args):  # which type should command have here?
        pass


class AggregatorClient():
    """ Send state changes to aggregator and execute commands from aggregator. Should possibly do async-to-sync via queue.
    Could possibly also just be queues for command input and tag/status output
    """

    def tag_updated(self, tag):  # includes blocks
        pass

    def code_line_updated(self, line_number: int):  # ?
        pass

    def on_command_request(self, cmd_name, cmd_args):
        pass

    #how about start/stop/pause/hold - are they commands or tags?


class EngineCommand():
    """ Represents a command request for engine to execute. """
    def __init__(self, name: str, args: str | None) -> None:
        self.name: str = name
        self.args: str | None = args


class Engine():
    """ Main engine class. Handles
    - io loop, reads and writes hardware process image (sync)
    - invokes interpreter if a program is loaded (sync, generator based)
    - signals state changes via tag_updates queue (to aggregator via websockets, natively async)
    - accepts commands from cmd_queue (from interpreter and from aggregator)
    """
    def __init__(self, uod: UnitOperationDefinitionBase) -> None:
        self.uod = uod
        self.started: bool = False
        self.system_tags = TagCollection.create_system_tags()  # TODO does the uod need to know about these?
        self.cmd_queue: Queue[EngineCommand] = Queue()  # hw commands to execute, coming from interpreter and from aggregator
        self.tag_updates: Queue[Tag] = Queue()  # tags updated in last tick
        self._tag_names_dirty: list[str] = []
        self.uod_listener = ChangeListener()

    def _iter_all_tags(self) -> Iterable[Tag]:
        return itertools.chain(self.system_tags, self.uod.tags)

    def _configure(self):
        # configure uod
        self.uod.define()
        self.uod.validate_configuration()
        self.uod.tags.add_listener(self.uod_listener)

    def run(self):
        self._configure()
        self._run()

    def _run(self, max_ticks=0):
        """ Starts the scan cycle """

        assert self.uod is not None
        assert self.uod.hwl is not None

        try:
            self.uod.hwl.connect()
        except HardwareLayerException:
            logger.error("Hardware connect error", exc_info=True)
            return  # TODO retry/reconnect

        self.started = True

        while self.started:
            self.tick()

            # TODO replace with OneThreadTimer for accurate timing
            time.sleep(0.1)

    def tick(self):
        """ Performs a scan cycle tick. """

        sys_tags = self.system_tags.clone()  # TODO clone does not currently support the subclasses
        uod_tags = self.uod.tags.clone()

        # read
        self.read_process_image()

        # execute commands

        # excecute interpreter tick

        self.execute_commands()

        # notify of tag changes
        self.notify_tag_updates()

        # write
        self.write_process_image()

    def read_process_image(self):
        """ Read data from hw into tags"""

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

        self.uod_listener.clear_changes()
        self._tag_names_dirty.clear()

        registers = hwl.registers
        register_values = hwl.read_batch(list(registers.values()))
        for i, r in enumerate(registers.values()):
            tag = self.uod.tags.get(r.name)
            tag_value = register_values[i]
            if "to_tag" in r.options:
                tag_value = r.options["to_tag"](tag_value)
            tag.set_value(tag_value)
            # self._tags_dirty.append(tag)

        self._tag_names_dirty = self.uod_listener.changes

    def execute_commands(self):
        while self.cmd_queue.qsize() > 0:
            try:
                c = self.cmd_queue.get()
                self._execute_command(c)
            except Empty:
                break

        self._tag_names_dirty = self.uod_listener.changes
        self.uod_listener.clear_changes()

    def _execute_command(self, cmd_request: EngineCommand):
        logger.debug("Executing command request: " + cmd_request.name)
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

    def notify_tag_updates(self):
        for tag_name in self._tag_names_dirty:
            tag = self.uod.tags[tag_name]
            self.tag_updates.put(tag)

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