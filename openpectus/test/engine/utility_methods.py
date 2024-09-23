from contextlib import contextmanager
import logging
import time
from typing import Callable, Generator, Literal
from openpectus.engine.models import EngineCommandEnum

from openpectus.lang.exec.runlog import RuntimeRecordStateEnum
from openpectus.lang.exec.tag_lifetime import BlockInfo, TagContext, TagLifetime
from openpectus.lang.exec.timer import TestTimerClock
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine, EngineTiming
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram


logger = logging.getLogger(__name__)


def build_program(s, skip_enrich_analyzers=False) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model(skip_enrich_analyzers=skip_enrich_analyzers)


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
    "Stop", "Restart"
]
""" Defines the awaitable instructions of the test engine runner """

FindInstructionState = Literal[
    "any", "started", "completed", "failed", "cancelled"
]
""" Defines the awaitable instruction states of the test engine runner """


class EngineTestInstance(TagLifetime):
    def __init__(self, engine: Engine, pcode: str, timing: EngineTiming) -> None:
        self.engine = engine
        self.timing = timing

        self.engine.run(skip_timer_start=True)
        self.set_method(pcode)

        self._search_index = 0
        self.engine.tag_context.add_listener(self)  # register as listener for lifetime events, so they can be awaited
        self._last_event: EventName | None = None



    def set_method(self, pcode: str):
        method = Mdl.Method.from_pcode(pcode)
        self.engine.set_method(method)

    def start(self):
        #self.engine._running = True
        self.engine.schedule_execution(EngineCommandEnum.START)
        self.timing.timer.start()

    @property
    def marks(self) -> list[str]:
        return self.engine.interpreter.get_marks()

    # def stop(self):
    #     pass

    # def pause(self):
    #     pass

    # def unpause(self):
    #     pass

    # def destroy(self):
    #     pass

    # def halt(self):
    #     """ Halt engine temporarily by stopping the tick timer. This also stops Clock time. """
    #     # TODO stop Clock time ...
    #     self.timer.pause()

    # def unhalt(self):
    #     """ Resume halted engine. """
    #     self.timer.resume()

    def run_until_condition(self, condition: RunCondition, max_ticks=30) -> int:
        """ Continue program until condition occurs. Return the number of ticks spent.

        Raises TimeoutError if the condition is not met before max_ticks is reached.
        """
        if condition():
            return 0
        ticks = 0
        max_ticks_scaled = max_ticks * self.timing.speed
        #self.unhalt()
        engine_tick = self.engine._tick_number
        while not condition():
            ticks += 1
            if ticks > max_ticks_scaled:
                if max_ticks == max_ticks_scaled:
                    raise TimeoutError(f"Condition did not occur within {max_ticks} ticks")
                else:
                    raise TimeoutError(
                        f"Condition did not occur within {max_ticks_scaled} ticks, " +
                        "(scaled from {max_ticks} using speed {self.speed})"
                    )

            while self.engine._tick_number == engine_tick:
                time.sleep(self.timing.interval * 0.3)  # this low seems to make test runs consistent
                #time.sleep(self.timing.interval * 0.1)  # this low seems to make test runs consistent

                # TODO this is not great - possibly use an observer approach instead
            engine_tick = self.engine._tick_number
        return ticks

    def run_until_instruction(
            self,
            instruction_name:
            InstructionName,
            state: FindInstructionState = "any",
            max_ticks=30,
            ) -> int:
        """ Continue program execution and wait until the given instruction is run.

        Use the `state` argument to specify how to wait. The default is 'any' which waits for any record for
        the given instruction. Note that for some instructions this happens much earlier than the start state,
        e.g. for Watch. This can be changed to e.g. `started` to wait until the instruction is started.

        Return the number of ticks spent.

        Raises TimeoutError if the instruction is not found before max_ticks is reached.
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

        def cond() -> bool:
            index = self.engine.runtimeinfo.find_instruction(instruction_name, self._search_index, request_state)
            if index is None:
                return False
            else:
                # store position so we only search from there next time
                # print(f"Found {instruction_name} at index {index}")
                self._search_index = index + 1
                if instruction_name == "Restart":  # except if restarting in which case we start over
                    self._search_index = 0
                return True

        logger.debug(f"Start waiting for instruction {instruction_name}")
        ticks = self.run_until_condition(cond, max_ticks=max_ticks)
        logger.debug(f"Done waiting for instruction {instruction_name}")
        return ticks

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
        return self.run_until_condition(cond, max_ticks=max_ticks)

    def get_runtime_table(self, description: str = "") -> str:
        """ Return a text view of the runtime table contents. """
        return self.engine.runtimeinfo.get_as_table(description)

    # --- TagLifetime impl ----


    def on_engine_configured(self, context: TagContext):
        self._last_event = None

    def on_start(self, context: TagContext):
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

    # --- TagLifetime end ----

class EngineTestRunner:
    """ Expose an interface of Engine similar to what is available in the frontend to tests. """
    def __init__(self, uod_factory: UodFactory, pcode: str = "", interval: float = 0.1, speed: float = 1.0) -> None:
        self.uod_factory = uod_factory
        self.pcode = pcode
        self.interval = interval
        self.speed = speed
        logger.debug(f"Created engine test runner, speed: {self.speed:.2f}, interval: {(self.interval*1000):.2f}ms")

    @contextmanager
    def run(self) -> Generator[EngineTestInstance, None, None]:
        timer = TestTimerClock(self.interval, self.speed)        
        timing = EngineTiming(timer, timer, self.interval, self.speed)
        uod = self.uod_factory()
        engine = Engine(uod, timing)
        instance = EngineTestInstance(engine, self.pcode, timing)
        try:
            yield instance
        except Exception:
            raise
        finally:
            timer.stop()
            engine.cleanup()
            del timer
            del instance


def run_engine(engine: Engine, pcode: str, max_ticks: int = -1):
    print("Interpretation started")
    ticks = 0
    max_ticks = max_ticks

    engine._running = True
    engine.set_method(Mdl.Method.from_pcode(pcode=pcode))
    engine.schedule_execution(EngineCommandEnum.START)

    while engine.is_running():
        ticks += 1
        if max_ticks != -1 and ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            return

        tick_time = time.time()
        time.sleep(0.1)
        engine.tick(tick_time, 0.1)

def continue_engine(engine: Engine, max_ticks: int = -1):
    # This function (as well as run_engine) differs from just calling engine.tick() in that
    # it passes the time before calling tick(). Some functionality depends on this, such as
    # thresholds.

    # TODO consider adding a SystemClock abstraction to avoid the need for waiting
    # in tests
    print("Interpretation continuing")
    ticks = 0
    max_ticks = max_ticks

    engine._running = True

    while engine.is_running():
        ticks += 1
        if max_ticks != -1 and ticks > max_ticks:
            print(f"Stopping because max_ticks {max_ticks} was reached")
            return

        tick_time = time.time()
        time.sleep(0.1)
        engine.tick(tick_time, 0.1)

def continue_engine_until(engine: Engine, condition: Callable[[int], bool], fail_ticks=30) -> int:
    print("Interpretation continuing")
    tick = 0
    engine._running = True

    while engine.is_running():
        if condition(tick):
            print(f"Stopping at tick {tick} because condition was True")
            return tick
        if tick >= fail_ticks:
            print("Failing because condition did not occur before max_ticks was reached")
            raise TimeoutError("Condition did not occur before max_ticks was reached")

        tick_time = time.time()
        time.sleep(0.1)
        engine.tick(tick_time, 0.1)
        tick += 1

    raise RuntimeError("Engine stopped for no good reason")

def print_runlog(e: Engine, description=""):
    runlog = e.interpreter.runtimeinfo.get_runlog()
    print(f"Runlog {runlog.id} records: ", description)
    #    print("line | start | end   | name                 | states")
    #    print("-----|-------|-------|----------------------|-------------------")
    for item in runlog.items:
        name = f"{str(item.name):<20}"
        prog = f"{item.progress:d2}" if item.progress else ""
        print(f"{name}   {item.state:<15}    {prog}")
#    print("-----|-------|-------|----------------------|-------------------")

def print_runtime_records(e: Engine, description: str = ""):
    table = e.interpreter.runtimeinfo.get_as_table()
    print(table)


def configure_test_logger():
    logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')


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


def set_interpreter_debug_logging():
    logger = logging.getLogger("openpectus.lang.exec.pinterpreter")
    logger.setLevel(logging.DEBUG)
