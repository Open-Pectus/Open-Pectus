from __future__ import annotations
from contextlib import contextmanager
import logging
import time
from typing import Callable, Generator, Literal
from openpectus.engine.method_manager import MethodManager
from openpectus.engine.models import EngineCommandEnum

from openpectus.lang.exec.clock import WallClock
from openpectus.lang.exec.errors import EngineError
from openpectus.lang.exec.runlog import RuntimeRecordStateEnum
from openpectus.lang.exec.events import BlockInfo, EventListener
from openpectus.lang.exec.timer import NullTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine, EngineTiming
import openpectus.lang.model.ast as p
from openpectus.lang.model.parser import ParserMethod, create_method_parser

logger = logging.getLogger(__name__)


def build_program(pcode: str) -> p.ProgramNode:
    method = ParserMethod.from_pcode(pcode)
    parser = create_method_parser(method)
    return parser.parse_method(method)


UodFactory = Callable[[], UnitOperationDefinitionBase]

RunCondition = Callable[[], bool]

EventName = Literal[
    "start", "stop", "block_start", "block_end",
    "restart", "pause", "hold",
    "method_end"
]
""" Defines the awaitable events of the test engine runner """

InstructionName = Literal[
    "Block", "End block", "End blocks",
    "Watch", "Alarm", "Mark",
    "Pause", "Hold", "Wait",
    "Stop", "Restart",
    "Info", "Warning", "Error",
    "Macro", "Call macro",
    "Increment run counter",
    "Noop", "Notify",
    "Simulate", "Simulate off"
]
""" Defines the awaitable instructions of the test engine runner """

FindInstructionState = Literal[
    "any", "started", "completed", "failed", "cancelled",
    "awaiting_threshold", "awaiting_condition",
]
""" Defines the awaitable instruction states of the test engine runner """


class EngineTestRunner:
    """ Expose an interface of Engine similar to what is available in the frontend to tests. """
    def __init__(self, uod_factory: UodFactory, method: str | Mdl.Method = "", interval: float = 0.1, speed: float = 1.0)\
            -> None:
        self.uod_factory = uod_factory
        self.method: str | Mdl.Method = method
        self.interval = interval
        self.speed = speed
        logger.debug(f"Created engine test runner, speed: {self.speed:.2f}, interval: {(self.interval*1000):.2f}ms")

    @contextmanager
    def run(self) -> Generator[EngineTestInstance, None, None]:
        timing = EngineTiming(WallClock(), NullTimer(), self.interval, self.speed)
        uod = self.uod_factory()
        engine = Engine(uod, timing)
        instance = EngineTestInstance(engine, self.method, timing)
        try:
            yield instance
        except Exception:
            raise
        finally:
            engine.cleanup()
            del instance


class EngineTestInstance(EventListener):
    def __init__(self, engine: Engine, method: str | Mdl.Method, timing: EngineTiming) -> None:
        self.engine = engine
        self.timing = timing

        self.engine.run(skip_timer_start=True)
        if isinstance(method, str):
            method = Mdl.Method.from_pcode(method)
        self.engine.set_method(method)

        self._search_index = 0
        # register as listener for lifetime events, so these events can be awaited in the tests
        self.engine.emitter.add_listener(self)
        self._last_event: EventName | None = None

    def start(self):
        """ Schedules the Start command. run_* is required to actually run it """
        self.engine.schedule_execution(EngineCommandEnum.START)
        self.timing.timer.start()

    @property
    def marks(self) -> list[str]:
        return self.engine.interpreter.get_marks()

    @property
    def method_manager(self) -> MethodManager:
        return self.engine.method_manager

    def run_until_condition(self, condition: RunCondition, max_ticks=30) -> int:
        """ Continue program until condition occurs. Return the number of ticks spent.

        Raises TimeoutError if the condition is not met before max_ticks is reached.
        """
        if condition():
            return 0

        ticks = 0
        max_ticks_scaled = max_ticks * self.timing.speed
        last_tick_time = 0.0

        while not condition():
            tick_time = time.time()

            ticks += 1
            if ticks > max_ticks_scaled:
                if max_ticks == max_ticks_scaled:
                    raise TimeoutError(f"Condition did not occur within {max_ticks} ticks")
                else:
                    raise TimeoutError(
                        f"Condition did not occur within {max_ticks_scaled} ticks, " +
                        "(scaled from {max_ticks} using speed {self.speed})"
                    )
            increment = self.timing.interval
            if last_tick_time > 0.0:
                increment = tick_time - last_tick_time
                self.engine.tick(tick_time, increment)

            last_tick_time = tick_time
            elapsed = time.time() - last_tick_time
            deadline = self.timing.interval - elapsed
            if deadline > 0.0:
                while last_tick_time+self.timing.interval-time.time() > 0:
                    time.sleep(min(last_tick_time+self.timing.interval-time.time(), 0.01))
            else:
                logger.warning(f"Sleep deadline for tick was negative: {deadline}")

            if self.engine.has_error_state():
                ex = self.engine.get_error_state_exception()
                if ex is None:
                    raise EngineError("Engine failed with an unspecified error")
                else:
                    raise EngineError(f"Engine failed with exception: {ex}", exception=ex)

        return ticks

    def run_until_instruction(  # noqa C901
            self,
            instruction_name: InstructionName,
            state: FindInstructionState = "any",
            arguments: str | None = None,
            max_ticks=30,
            increment_index=True
            ) -> int:
        """ Continue program execution and wait until the given instruction is run.

        Use the `state` argument to specify how to wait. The default is 'any' which waits for any record for
        the given instruction. Note that for some instructions this happens much earlier than the start state,
        e.g. for Watch. This can be changed to e.g. `started` to wait until the instruction is started.

        Return the number of ticks spent.

        Raises TimeoutError if the instruction is not found before max_ticks is reached.

        Use `increment_index` to control searching within states of the same instruction as last search. The default
        value of True skips to the next instruction which is normally what you want. If set to False, search also
        includes the record of the previous match. This is useful if searching for different states for the same
        record, such as "started" and "completed". See also `index_step_back()`.
        """

        # convert the easy-to-use literal into one of the enum states that find_instruction needs
        request_state: RuntimeRecordStateEnum | None = None
        if state != "any":
            if state == "started":
                request_state = RuntimeRecordStateEnum.Started
            elif state == "completed":
                request_state = RuntimeRecordStateEnum.Completed
            elif state == "failed":
                request_state = RuntimeRecordStateEnum.Failed
            elif state == "cancelled":
                request_state = RuntimeRecordStateEnum.Cancelled
            elif state == "awaiting_threshold":
                request_state = RuntimeRecordStateEnum.AwaitingThreshold
            elif state == "awaiting_condition":
                request_state = RuntimeRecordStateEnum.AwaitingCondition
            elif state == "awaiting_interrupt":
                request_state = RuntimeRecordStateEnum.AwaitingInterrrupt

        def cond() -> bool:
            index = self.engine.runtimeinfo.find_instruction(instruction_name, arguments, self._search_index, request_state)
            if index is None:
                return False
            else:
                # store position so we only search from there next time
                # print(f"Found {instruction_name} at index {index}")
                self._search_index = index + 1 if increment_index else index
                if instruction_name == "Restart":  # except if restarting in which case we start over
                    self._search_index = 0
                return True

        logger.debug(f"Start waiting for instruction {instruction_name}, state: {state}, arguments: {arguments}")
        try:
            ticks = self.run_until_condition(cond, max_ticks=max_ticks)
        except TimeoutError:
            raise TimeoutError(
                f"Timeout while waiting for instruction '{instruction_name}', state: {state}, arguments: {arguments}")

        logger.debug(f"Done waiting for instruction {instruction_name}, state: {state}, arguments: {arguments}. " +
                     f"Duration: {ticks} ticks.")
        return ticks

    def index_step_back(self, steps=1):
        # Not a good abstraction. Specifically not for alarms
        # the best way would be to maintain a index for each runtime record
        # os use tick as index, then search all records from there. That eliminates
        # the use of an index alltogether - but does slow it down, though, as it
        # has to search all records on every query.
        if steps < 1:
            raise ValueError("Steps must be positive")
        if self._search_index - steps < 0:
            self._search_index = 0
        else:
            self._search_index = self._search_index - steps

    def _clear_last_event(self):
        self._last_event = None

    def run_until_event(self, event_name: EventName, max_ticks=100) -> int:
        """ Continue program execution and wait until the given event fires.

        Return the number of ticks spent.

        Raises TimeoutError if the instruction is not found before max_ticks is reached.
        """
        def cond():
            if self._last_event == event_name:
                self._clear_last_event()
                return True
            else:
                return False
        try:
            return self.run_until_condition(cond, max_ticks=max_ticks)
        except TimeoutError:
            raise TimeoutError(f"Timeout while waiting for event '{event_name}'")

    def restart_and_run_until_started(self) -> None:
        """ Restart the method and wait a few ticks for engine to come back up. """
        self.engine.schedule_execution(EngineCommandEnum.RESTART)
        self._search_index = 0
        self._last_event = None
        self.run_ticks(1)
        while self._last_event is None or self._last_event != "start":
            print("Waiting for started event")
            self.run_ticks(1)

    def run_ticks(self, ticks: int) -> None:
        """ Continue program execution until te specified number of ticks. """

        logger.debug(f"Start waiting for {ticks} ticks")
        max_ticks = ticks + 1
        try:
            _ = self.run_until_condition(lambda: False, max_ticks)
        except TimeoutError:
            logger.debug(f"Done waiting for {ticks} ticks")
            return

        raise ValueError("Could not wait??")

    def get_runtime_table(self, description: str = "") -> str:
        """ Return a text view of the runtime table contents. """
        return self.engine.runtimeinfo.get_as_table(description)

    # --- EventListener impl ----

    def on_engine_configured(self):
        self._last_event = None

    def on_start(self, run_id: str):
        self._last_event = "start"

    def on_block_start(self, block_info: BlockInfo):
        self._last_event = "block_start"

    def on_block_end(self, block_info: BlockInfo, new_block_info: BlockInfo | None):
        self._last_event = "block_end"

    def on_tick(self, tick_time: float, increment_time: float):
        pass

    def on_method_end(self):
        self._last_event = "method_end"

    def on_stop(self):
        self._last_event = "stop"

    def on_engine_shutdown(self):
        pass

    # --- EventListener end ----


# globals for run_engine and continue_engine
last_tick_time = 0.0
interval = 0.1


def run_engine(engine: Engine, pcode: str, max_ticks: int = -1) -> int:
    global last_tick_time, interval
    print("Interpretation started")
    engine._running = True
    engine.set_method(Mdl.Method.from_pcode(pcode=pcode))
    engine.schedule_execution(EngineCommandEnum.START)

    ticks = 1
    last_tick_time = 0.0

    while True:
        tick_time = time.time()

        if ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            return ticks

        increment = 0.0
        if last_tick_time > 0.0:
            increment = tick_time - last_tick_time

        # execute tick even with 0 increment
        engine.tick(tick_time, increment)

        last_tick_time = tick_time
        elapsed = time.time() - last_tick_time
        deadline = interval - elapsed
        if deadline > 0.0:
            while last_tick_time+interval-time.time() > 0:
                time.sleep(min(last_tick_time+interval-time.time(), 0.01))
        else:
            logger.warning(f"Sleep deadline for tick was negative: {deadline}")

        if engine.has_error_state():
            ex = engine.get_error_state_exception()
            if ex is None:
                raise EngineError("Engine failed with an unspecified error")
            else:
                raise EngineError(f"Engine failed with exception: {ex}", exception=ex)

        ticks += 1


def continue_engine(engine: Engine, max_ticks: int = -1) -> int:
    global last_tick_time, interval
    print("Interpretation continuing")
    ticks = 1

    while True:
        tick_time = time.time()

        if ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            return ticks

        increment = 0
        if last_tick_time > 0.0:
            increment = tick_time - last_tick_time

        # execute tick even with 0 increment
        engine.tick(tick_time, increment)

        last_tick_time = tick_time
        elapsed = time.time() - last_tick_time
        deadline = interval - elapsed
        if deadline > 0.0:
            while last_tick_time+interval-time.time() > 0:
                time.sleep(min(last_tick_time+interval-time.time(), 0.01))
        else:
            logger.warning(f"Sleep deadline for tick was negative: {deadline}")

        if engine.has_error_state():
            ex = engine.get_error_state_exception()
            if ex is None:
                raise EngineError("Engine failed with an unspecified error")
            else:
                raise EngineError(f"Engine failed with exception: {ex}", exception=ex)

        ticks += 1


def print_runlog(e: Engine, description=""):
    runlog = e.interpreter.runtimeinfo.get_runlog()
    print(f"Runlog {runlog.id} records: ", description)
    for item in runlog.items:
        name = f"{str(item.name):<20}"
        prog = f"{item.progress:.2f}" if item.progress else ""
        print(f"{name}   {item.state:<15}    {prog}")


def print_runtime_records(e: Engine, description: str = ""):
    table = e.interpreter.runtimeinfo.get_as_table(description)
    print(table)

def clear_log_config():
    """ Remove any existing logging setup, eg. from logging.basicConfig()"""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def configure_test_logger():
    clear_log_config()
    logging.basicConfig(format='%(name)s : %(levelname)-6s : %(message)s')


def set_engine_debug_logging():
    engine_modules = [
        "openpectus.engine.engine",
        # "openpectus.engine.internal_commands",
        "openpectus.engine.internal_commands_impl",
        __name__
    ]
    for m in engine_modules:
        logger = logging.getLogger(m)
        logger.setLevel(logging.DEBUG)


def set_interpreter_debug_logging(include_events=False, include_runlog=False):
    logger = logging.getLogger("openpectus.lang.exec.pinterpreter")
    logger.setLevel(logging.DEBUG)

    if include_runlog:
        logging.getLogger("openpectus.lang.exec.runlog").setLevel(logging.DEBUG)
    if include_events:
        logging.getLogger("openpectus.lang.exec.events").setLevel(logging.DEBUG)
        logging.getLogger("openpectus.lang.exec.tags_impl").setLevel(logging.DEBUG)
