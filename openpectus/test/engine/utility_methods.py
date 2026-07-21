from __future__ import annotations
from contextlib import contextmanager
import logging
from logging import LogRecord, Handler
import time
from typing import Callable, Generator, Literal

from openpectus.engine.method_manager import MethodManager
from openpectus.engine.models import EngineCommandEnum
from openpectus.lang.exec.clock import WallClock
from openpectus.lang.exec.errors import EngineError
from openpectus.lang.exec.runlog import RuntimeInfo, RuntimeRecordStateEnum
from openpectus.lang.exec.events import BlockInfo, EventListener, ScopeInfo
from openpectus.lang.exec.timer import NullTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
from openpectus.lang.exec.pinterpreter import PInterpreter
from openpectus.lang.exec.interpreter_models import SePath
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine, EngineTiming
import openpectus.lang.model.ast as p
from openpectus.lang.model.parser import ParserMethod, create_method_parser

logger = logging.getLogger(__name__)


def build_program(pcode: str) -> p.ProgramNode:
    method = ParserMethod.from_pcode(pcode)
    parser = create_method_parser(method)
    return parser.parse_method(method)

def _handle_engine_error(engine: Engine):
    ex = engine.get_error_state_exception()
    if ex is None:
        raise EngineError("Engine failed with an unspecified error")
    else:
        raise EngineError(f"Engine failed with exception: {ex}") from ex


UodFactory = Callable[[], UnitOperationDefinitionBase]
UodInstanceOrFactory = UnitOperationDefinitionBase | UodFactory

RunCondition = Callable[[], bool]

EventName = Literal[
    "start", "stop", "block_start", "block_end",
    "restart", "pause", "hold",
    "method_end", "method_edited"
]
""" Defines the awaitable events of the test engine runner """

InstructionName = Literal[
    "Block", "End block", "End blocks",
    "Watch", "Alarm", "Mark",
    "Pause", "Hold", "Wait",
    "Stop", "Restart",
    "Info", "Warning", "Error",
    "Macro", "Call macro",
    "Increment run counter", "Base",
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
    def __init__(self, uod_argument: UodInstanceOrFactory, method: str | Mdl.Method = "", interval: float = 0.1, speed: float = 1.0,
                 fail_on_log_error=True,
                 raise_on_emit=False
        ) -> None:
        """ Create an engine test runner instance.

        Args:
            method: Method to run. The format should be either raw pcode, numbered pcode or pre-parsed
        """
        self.uod_factory = (lambda: uod_argument) if isinstance(uod_argument, UnitOperationDefinitionBase) else uod_argument
        self.method: str | Mdl.Method = method
        self.interval = interval
        self.speed = speed
        self.error_log_handler = TestLogHandler(
            enabled=fail_on_log_error,
            auto_register=False,
            raise_on_emit=raise_on_emit
        )

        logger.debug(f"Created engine test runner, speed: {self.speed:.2f}, interval: {(self.interval*1000):.2f}ms")

    @contextmanager
    def run(self) -> Generator[EngineTestInstance, None, None]:
        timing = EngineTiming(WallClock(), NullTimer(), self.interval, self.speed)
        uod = self.uod_factory()
        engine = Engine(uod, timing)
        instance = EngineTestInstance(engine, self.method, timing)
        self.error_log_handler.register()
        try:
            yield instance
            self.error_log_handler.raise_if_errors_encountered()
        except Exception:
            raise
        finally:
            engine.cleanup()
            del instance
            self.error_log_handler.unregister()

class EngineTestInstance(EventListener):
    def __init__(self, engine: Engine, method: str | Mdl.Method, timing: EngineTiming) -> None:
        self.engine = engine
        self.timing = timing

        # The time increment value to use for the first iteration of run_until_*() methods where the previous tick time is not defined.
        # Using interval makes timing more natural than when using a value of 0.
        #
        # The concept at play is that tags and other event consumers use the 'increment_time' argument of the on_tick event to
        # determine time passed. This allows pausing time in various ways, eg. the Pause instruction or timers going in and out of
        # scope. Whenever the run is continued, the first tick must use a 'last value' to calculate increment_time and this value
        # must be constructed to avoid including the pause duration in increment_time (which would cause a large and incorrect spike
        # in the time perceived by the tag).
        #
        # In the production code, this is different because increment_time is zero on first tick and then never again and tags handle
        # 'pause' to determine when to increment their timers. But in tests there is an implicit pause whenever a run_until_* method
        # ends so the next run_until_* method must use a proper value for increment_time.
        self._initial_increment = self.timing.interval

        self.engine.run(skip_timer_start=True)
        if isinstance(method, str):
            if Mdl.Method.is_probably_numbered_pcode(method):
                method = Mdl.Method.from_numbered_pcode(method)
            else:
                method = Mdl.Method.from_pcode(method)

        self.engine.set_method(method)

        self._search_index = 0
        # register as listener for lifetime events, so these events can be awaited in the tests
        self.add_event_listener(self)
        self._last_event: EventName | None = None
        self._scopes: list[ScopeInfo] = []
        self._scope_history: list[ScopeInfo] = []

    def start(self):
        """ Schedules the Start command. run_* is required to actually run it """
        self.engine.schedule_execution(EngineCommandEnum.START)
        self.timing.timer.start()

    def start_run(self):
        """ Start a run making the runner ready for normal operation. """
        assert self.engine._tick_number == -1
        self.start()
        self.run_ticks(1)
        assert self.engine._tick_number == 0

    def add_event_listener(self, listener: EventListener):
        self.engine.emitter.add_listener(listener)

    @property
    def marks(self) -> list[str]:
        return self.engine.interpreter.get_marks()

    @property
    def method_manager(self) -> MethodManager:
        return self.engine.method_manager

    @property
    def runtimeinfo(self) -> RuntimeInfo:
        return self.engine.interpreter.runtimeinfo

    @property
    def scope_node_id(self) -> str | None:
        if len(self._scopes) > 0:
            return self._scopes[-1].node_id
        return None

    @property
    def scope_node_ids(self) -> list[str]:
        return [scope.node_id for scope in self._scopes]

    @property
    def scope_node_history(self) -> list[str]:
        return list([scope.node_id for scope in self._scope_history])

    def run_ticks(self, ticks: int, verbose=True, fail_on_log_error=True) -> int:
        """ Continue program execution for the specified number of ticks. """

        if verbose:
            logger.info(f"Start waiting for {ticks} ticks")

        error_log_handler = TestLogHandler(enabled=fail_on_log_error)

        tick_index = 0
        last_tick_time_mon = 0.0
        increment = self._initial_increment
        interval = self.timing.interval

        while tick_index < ticks:
            tick_time = time.time()
            tick_time_mon = time.monotonic()
            if tick_index > 0:
                increment = tick_time_mon - last_tick_time_mon

            # execute tick, with increment==0 on first iteration
            self.engine.tick(tick_time, increment)

            # # wait random time 1-10 times a tenth of a tick to stress test duration calculation
            #secs = random.randint(0, 10) * 0.1 * 0.1
            #logger.info(f"Sleeping {secs}")
            #time.sleep(secs)

            self._handle_error(error_log_handler)

            last_tick_time_mon = tick_time_mon
            tick_time_mon = time.monotonic()
            elapsed = tick_time_mon - last_tick_time_mon
            deadline = interval - elapsed
            if deadline > 0.001:
                time.sleep(deadline)
            elif deadline < 0:
                logger.warning(f"Sleep deadline for tick was negative: {deadline}")

            tick_index += 1

        if verbose:
            logger.info(f"Done waiting for {ticks} ticks")
        return tick_index


    def run_until_condition(self, condition: RunCondition, max_ticks=30, fail_on_log_error=True) -> int:
        """ Continue program until condition occurs. Return the number of ticks spent.

        Raises TimeoutError if the condition is not met before max_ticks is reached.
        """
        if condition():
            return 0

        error_log_handler = TestLogHandler(enabled=fail_on_log_error)

        tick_index = 0
        last_tick_time_mon = 0.0
        increment = self._initial_increment
        interval = self.timing.interval

        while True:
            tick_time = time.time()
            tick_time_mon = time.monotonic()
            if tick_index > 0:
                increment = tick_time_mon - last_tick_time_mon

            if condition():
                return tick_index

            if tick_index >= max_ticks:
                raise TimeoutError(f"Condition did not occur within {max_ticks} ticks")

            # execute tick, with increment==0 on first iteration
            self.engine.tick(tick_time, increment)

            self._handle_error(error_log_handler)

            last_tick_time_mon = tick_time_mon
            tick_time_mon = time.monotonic()
            elapsed = tick_time_mon - last_tick_time_mon
            deadline = interval - elapsed
            if deadline > 0.001:
                time.sleep(deadline)
                # If doing this again, must use last_tick_time_mon
                # while last_tick_time + interval - time.time() > 0:
                #     time.sleep(min(last_tick_time + interval - time.time(), 0.01))
            elif deadline < 0:
                logger.warning(f"Sleep deadline for tick was negative: {deadline}")

            tick_index += 1

    def _handle_error(self, test_log_handler: TestLogHandler):
        if self.engine.has_error_state():
            _handle_engine_error(self.engine)
        else:
            test_log_handler.raise_if_errors_encountered()

    def _convert_FindInstruction_state_to_enum(self, state: FindInstructionState) -> RuntimeRecordStateEnum | None:
        # convert the easy-to-use literal into one of the enum states that find_instruction needs
        if state == "any":
            return None
        elif state == "started":
            return RuntimeRecordStateEnum.Started
        elif state == "completed":
            return RuntimeRecordStateEnum.Completed
        elif state == "failed":
            return RuntimeRecordStateEnum.Failed
        elif state == "cancelled":
            return RuntimeRecordStateEnum.Cancelled
        elif state == "awaiting_threshold":
            return RuntimeRecordStateEnum.AwaitingThreshold
        elif state == "awaiting_condition":
            return RuntimeRecordStateEnum.AwaitingCondition
        else:
            raise NotImplementedError(f"Searching for instruction state '{state}' is not supported")

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

        Note: Some instructions have special behavior, most notable Restart that restarts the engine which resets the
        record state in which we search. Effectively, it only supports waiting with no state provided. Start and Stop
        have similar quirks.

        Use `increment_index` to control searching within states of the same instruction as last search. The default
        value of True skips to the next instruction which is normally what you want. If set to False, search also
        includes the record of the previous match. This is useful if searching for different states for the same
        record, such as "started" and "completed". See also `index_step_back()`.
        """
        request_state = self._convert_FindInstruction_state_to_enum(state)
        if request_state is not None and instruction_name == EngineCommandEnum.RESTART:
            raise ValueError("For the Restart command, searching is only supported using the default any/None state")

        def cond() -> bool:
            index = self.runtimeinfo.find_instruction(instruction_name, arguments, self._search_index, request_state)
            if index is None:
                return False
            else:
                # store position so we only search from there next time
                # print(f"Found {instruction_name} at index {index}")
                self._search_index = index + 1 if increment_index else index
                if instruction_name == EngineCommandEnum.RESTART:  # except if restarting in which case we start over
                    self._search_index = 0
                return True

        logger.info(f"Start waiting for instruction {instruction_name}, state: {state}, arguments: {arguments}")
        try:
            ticks = self.run_until_condition(cond, max_ticks=max_ticks)
        except TimeoutError:
            logger.warning(self.get_runtime_table("At TimeoutError"))
            logger.warning(f"Timeout while waiting for instruction '{instruction_name}', state: {state}, arguments: {arguments}")
            raise TimeoutError(
                f"Timeout while waiting for instruction '{instruction_name}', state: {state}, arguments: {arguments}")

        logger.info(f"Done waiting for instruction {instruction_name}, state: {state}, arguments: {arguments}. " +
                    f"Duration: {ticks} ticks.")
        return ticks

    def run_until_command(  # noqa C901
            self,
            command_name: str,
            state: FindInstructionState = "any",
            arguments: str | None = None,
            max_ticks=30,
            increment_index=True
            ) -> int:

        request_state = self._convert_FindInstruction_state_to_enum(state)
        if request_state is not None and command_name == "Restart":
            raise ValueError("For the Restart command, searching is only supported using the default 'any' state")

        def cond() -> bool:
            index = self.runtimeinfo.find_command(command_name, arguments, self._search_index, request_state)
            if index is None:
                return False
            else:
                # store position so we only search from there next time
                # print(f"Found {instruction_name} at index {index}")
                self._search_index = index + 1 if increment_index else index
                if command_name == "Restart":  # except if restarting in which case we start over
                    self._search_index = 0
                return True

        logger.info(f"Start waiting for command {command_name}, state: {state}, arguments: {arguments}")
        try:
            ticks = self.run_until_condition(cond, max_ticks=max_ticks)
        except TimeoutError:
            raise TimeoutError(
                f"Timeout while waiting for command {command_name}, state: {state}, arguments: {arguments}")

        logger.info(f"Done waiting for command {command_name}, state: {state}, arguments: {arguments}. " +
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

    def get_runtime_table(self, description: str = "") -> str:
        """ Return a text view of the runtime table contents. """
        return self.runtimeinfo.get_as_table(description)

    @property
    def logger(self):
        return logger

    def print_runtime_table(self, description=""):
        """ Print a text view of the runtime table contents. """
        table = self.runtimeinfo.get_as_table(description)
        print(table)

    def print_runlog(self, description=""):
        """ Print a text view of the runlog lines. """
        print_runlog(self.engine, description)

    # --- EventListener impl ----

    def on_engine_configured(self):
        self._last_event = None

    def on_start(self, run_id: str):
        self._last_event = "start"
        self._scopes.clear()

    def on_block_start(self, block_info: BlockInfo):
        self._last_event = "block_start"

    def on_block_end(self, block_info: BlockInfo, new_block_info: BlockInfo | None):
        self._last_event = "block_end"

    def on_scope_start(self, scope_info: ScopeInfo):
        if scope_info.node_id in self.scope_node_ids:
            logger.error(f"on_scope_start: Node {scope_info.node_id} is already in (a) scope")
        else:
            self._scopes.append(scope_info)
        self._scope_history.append(scope_info)

    def on_scope_activate(self, scope_info: ScopeInfo):
        if scope_info.node_id not in self.scope_node_ids:
            logger.error(f"on_scope_activate: Node {scope_info.node_id} is not in a started scope")

    def on_scope_end(self, scope_info: ScopeInfo):
        if scope_info.node_id not in self.scope_node_ids:
            logger.error(f"on_scope_end: Scope {scope_info} not in scopes. Actual scopes: {self._scopes}")
        else:
            self._scopes.remove(scope_info)

    def on_tick(self, tick_time: float, increment_time: float):
        pass

    def on_method_end(self):
        self._last_event = "method_end"

    def on_stop(self):
        self._last_event = "stop"

    def on_method_edited(self, live_edit: bool):
        self._last_event = "method_edited"
        self._search_index = 0

    def on_engine_shutdown(self):
        pass

    # --- EventListener end ----


# globals for run_engine and continue_engine
last_tick_time = 0.0
interval = 0.1


def run_engine(engine: Engine, pcode: str, max_ticks: int = -1, fail_on_log_error=True) -> int:
    global last_tick_time, interval
    print("Interpretation started")
    engine._running = True
    engine.set_method(Mdl.Method.from_pcode(pcode=pcode))
    engine.schedule_execution(EngineCommandEnum.START)

    error_log_handler = TestLogHandler(enabled=fail_on_log_error)
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
            _handle_engine_error(engine)
        else:
            error_log_handler.raise_if_errors_encountered()
        ticks += 1

def continue_engine(engine: Engine, max_ticks: int = -1, fail_on_log_error=True) -> int:
    global last_tick_time, interval
    print("Interpretation continuing")
    ticks = 1
    error_log_handler = TestLogHandler(enabled=fail_on_log_error)

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
            _handle_engine_error(engine)
        else:
            error_log_handler.raise_if_errors_encountered()
        ticks += 1

def continue_engine_until(engine: Engine, condition: Callable[[], bool], max_ticks: int = -1, fail_on_log_error=True) -> int:
    global last_tick_time, interval
    print("Interpretation continuing until condition")
    ticks = 1
    error_log_handler = TestLogHandler(enabled=fail_on_log_error)

    if condition():
        return 0

    while True:
        tick_time = time.time()

        if condition():
            print(f"Stopping because condition was True")
            return ticks

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
            _handle_engine_error(engine)
        else:
            error_log_handler.raise_if_errors_encountered()
        ticks += 1


def print_runlog(e: Engine, description=""):
    runlog = e.interpreter.runtimeinfo.get_runlog()
    print()
    print(f"Runlog {runlog.id} items | ", description)
    print("| ----------- instance_id ------------ | ---------- runlog name ---------- | -- state -- | progress | extras")
    for item in runlog.items:
        name = f"{str(item.name):<25}"
        progress = f"{item.progress:.2f}" if item.progress else ""
        extra_state = "forced" if item.forced else ("cancelled" if item.cancelled else "")
        print(f"  {item.id}   {name}           {item.state:<11}    {progress:<8}  {extra_state}")


def print_runtime_records(e: Engine, description: str = ""):
    table = e.interpreter.runtimeinfo.get_as_table(description)
    print(table)

def print_runtime_records_alt(e: Engine, description: str = ""):
    table = e.interpreter.runtimeinfo.get_as_table_alt(description)
    print(table)

def clear_log_config():
    """ Remove any existing logging setup, eg. from logging.basicConfig()"""
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

def configure_test_logger():
    clear_log_config()
    logging.basicConfig(format='%(name)s : %(levelname)-6s : %(message)s')


def set_engine_debug_logging():
    # seems necessary to get log items for internal_commands_impl
    import openpectus.engine.internal_commands_impl  # noqa: F401

    engine_modules = [
        "openpectus.engine.engine",
        # "openpectus.engine.internal_commands",
        "openpectus.engine.internal_commands_impl",
        "openpectus.engine.command_manager",
        __name__,
    ]
    for m in engine_modules:
        logger = logging.getLogger(m)
        logger.setLevel(logging.DEBUG)


def set_interpreter_debug_logging(include_events=False, include_runlog=False):
    logging.getLogger(PInterpreter.__module__).setLevel(logging.DEBUG)
    logging.getLogger(SePath.__module__).setLevel(logging.DEBUG)

    if include_runlog:
        logging.getLogger(RuntimeInfo.__module__).setLevel(logging.DEBUG)
    if include_events:        
        logging.getLogger(EventListener.__module__).setLevel(logging.DEBUG)
        logging.getLogger("openpectus.lang.exec.tags_impl").setLevel(logging.DEBUG)


class TestLogHandler(Handler):
    """ Log handler that is used during tests to discover errors being logged while tests run. """

    def __init__(self, enabled=True, auto_register=True, raise_on_emit=False):
        """Create new test log handler

        Parameters:
            enabled (bool, default True):
                If False, no exceptions are raised by the handler
            auto_register (bool, default True):
                If True, register is called just after creation. Set to False to call register at a later time
            raise_on_emit (bool, default False):
                If True, the handler raises as soon as the first error is logged. This can help in discovering
                the error location.
        """
        self.setLevel(logging.ERROR)
        self._errors: list[LogRecord] = []
        self.is_registered = False
        super().__init__()
        self.set_name(self.__class__.__name__)
        self.enabled = enabled
        self.raise_on_emit = raise_on_emit
        if auto_register:
            self.register()

    def emit(self, record):
        if record is None:
            raise TypeError("emit was called with a record value of None")
        if not isinstance(record, LogRecord):
            raise TypeError(f"emit was called with a record of unexpected type {type(record)}. Expected type LogRecord")
        if record.levelno >= logging.ERROR:
            # changed internal logs to warning - so no filtering is required
            # if record.name == __loader__.name:
            #     # skip TimeoutError and other internal errors so errors logged in this module 
            #     skip_funcs = ['run_until_instruction']
            #     if record.funcName in skip_funcs:
            #         return
            self._errors.append(record)

            if self.raise_on_emit:
                raise Exception(record.msg)

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0

    @property
    def errors(self) -> list[LogRecord]:
        return self._errors

    def _get_loggers(self) -> list[logging.Logger]:
        loggers = [logging.getLogger()]  # root logger
        loggers += [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        return loggers

    def register(self):
        self.is_registered = True
        self._errors.clear()
        loggers = self._get_loggers()
        for logger in loggers:
            logger.addHandler(self)

    def unregister(self):
        self.is_registered = False
        loggers = self._get_loggers()
        for logger in loggers:
            try:
                logger.removeHandler(self)
            except Exception as ex:
                print(f"Error in TestLogHandler during unregister for logger {logger.name}: {ex}")

    def raise_if_errors_encountered(self):
        """ Unregister and verify that no errors were logged. Raises Exception if one or more errors were logged. """
        if self.is_registered:
            self.unregister()
        if not self.enabled or not self.has_errors:
            return
        message = f"Errors were logged during the test, {len(self.errors)} errors in total.\n" +\
                  f"First error:\n{str(self.errors[0])}"
        raise Exception(message)
