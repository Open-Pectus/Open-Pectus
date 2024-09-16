from contextlib import contextmanager
import logging
import time
from typing import Callable, Generator, Literal
from openpectus.engine.models import EngineCommandEnum

from openpectus.lang.exec.clock import FixedSpeedTestClock
from openpectus.lang.exec.tag_lifetime import BlockInfo, TagContext, TagLifetime
from openpectus.lang.exec.tags import SystemTagName
from openpectus.lang.exec.timer import NullTimer, OneThreadTimer
from openpectus.lang.exec.uod import UnitOperationDefinitionBase
import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram


def build_program(s, skip_enrich_analyzers=False) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model(skip_enrich_analyzers=skip_enrich_analyzers)


EngineFactory = Callable[[], Engine]

RunCondition = Callable[[], bool]

EventName = Literal[
    "start", "stop", "block_start", "block_end",
    "restart", "pause", "hold"]

InstructionName = Literal[
    "Block", "End block", "End blocks",
    "Watch", "Alarm", "Mark",
    "Pause", "Hold", "Wait",
    "Stop", "Restart"
]

class EngineTestInstance(TagLifetime):
    def __init__(self, engine: Engine, pcode: str, speed: float) -> None:
        self.engine = engine

        self.engine.run()
        self.speed = speed
        interval = 0.1 / speed
        print(f"Creating engine test runner, speed: {speed:.2f}, interval: {(interval*1000):.2f}ms")

        self.timer = OneThreadTimer(interval, self._tick)
        engine._tick_timer = NullTimer()

        # self.clock = TestClock(time_per_tick=interval*speed)
        self.clock = FixedSpeedTestClock(speed=speed)
        # self.clock = WallClock()
        engine._clock = self.clock

        self.set_method(pcode)

        self.search_index = 0

        self.engine.tag_context.add_listener(self)
        self._last_event: EventName | None = None

        self.prev_ticks: list[float] = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.prev_index = -1
        self.prev_10 = False

    

    def _tick(self):
        #self.clock.increase_by_tick()

        # if self.sample % self.oversample == 0:
        #     self.engine.tick()
        #     self.sample = (self.sample + 1) % self.oversample

        self.engine.tick()

        time = self.clock.get_time()
        self.prev_index = (self.prev_index + 1) % 10
        self.prev_ticks[self.prev_index] = time
        if self.prev_index == 9:
            self.prev_10 = True
        
        if self.prev_10:
            s9_s0 = self.prev_ticks[9] - self.prev_ticks[0]
            print("Tick diff fot 10 ticks", s9_s0)
        
        # if self.last_time > 0:
        # TODO try to determine timer accuracy - every 10 consecutive frames should be very accurately 10*tick


    def set_method(self, pcode: str):
        method = Mdl.Method.from_pcode(pcode)
        self.engine.set_method(method)

    def start(self):
        self.engine._running = True
        self.engine.schedule_execution(EngineCommandEnum.START)
        self.timer.start()

    def stop(self):
        pass

    def pause(self):
        pass

    def unpause(self):
        pass

    def destroy(self):
        pass

    def halt(self):
        """ Halt engine temporarily by stopping the tick timer. This also stops Clock time. """
        # TODO stop Clock time ...
        self.timer.pause()

    def unhalt(self):
        """ Resume halted engine. """
        self.timer.resume()

    def run_until_condition(self, condition: RunCondition, max_ticks=30) -> int:
        """ Continue program until condition occurs. Return the number of ticks spent. """
        if condition():
            return 0
        ticks = 0
        max_ticks_scaled = max_ticks * self.speed
        #self.unhalt()
        engine_tick = self.engine._tick_number
        while not condition():
            ticks += 1
            if ticks > max_ticks_scaled:
                if max_ticks == max_ticks_scaled:
                    raise TimeoutError(f"Condition did not occur within {max_ticks} ticks")
                else:
                    raise TimeoutError(
                        f"Condition did not occur within {max_ticks_scaled} ticks " +
                        "(scaled from {max_ticks} using speed {self.speed})"
                    )

            while self.engine._tick_number == engine_tick:
                time.sleep(0.02)
            engine_tick = self.engine._tick_number
        return ticks

    def run_until_instruction(self, instruction_name: InstructionName, max_ticks=30) -> int:
        """ Continue program execution until immidiately before the start of the given instruction.

        Return the number of ticks spent.
        """
        def cond() -> bool:
            index = self.engine.runtimeinfo.find_instruction(instruction_name, self.search_index)
            if index is None:
                return False
            else:
                # store position so we only search from there next time
                # print(f"Found {instruction_name} at index {index}")
                self.search_index = index
                if instruction_name == "Restart":  # except if restarting in which case we start over
                    self.search_index = 0
                return True

        return self.run_until_condition(cond, max_ticks=max_ticks)

    def clear_last_event(self):
        self._last_event = None

    def run_until_event(self, event_name: EventName, max_ticks=100) -> int:
        def cond():
            if self._last_event == event_name:
                self.clear_last_event()
                return True
            else:
                return False
        return self.run_until_condition(cond, max_ticks=max_ticks)

    def get_runtime_table(self, description: str = "") -> str:
        return self.engine.runtimeinfo.get_as_table(description)

    # --- TagLifetime impl ----


    def on_engine_configured(self, context: TagContext):
        """ Invoked once on engine startup, after configuration and after
        the connection to hardware has been established. """
        self._last_event = None

    def on_start(self, context: TagContext):
        """ Is invoked by the Start command when method is started. """
        self._last_event = "start"

    def on_block_start(self, block_info: BlockInfo):
        """ Invoked just after a new block is started, before on_tick,
            in the same engine tick.
        """
        self._last_event = "block_start"

    def on_block_end(self, block_info: BlockInfo, new_block_info: BlockInfo | None):
        """ Invoked just after a block is completed, before on_tick,
        in the same engine tick. """
        self._last_event = "block_end"

    def on_tick(self, tick_time: float):
        """ Is invoked on each tick.

        Intended for NA (calculated/derived) tags to calculate the
        value for the tick and apply it to the value property. """
        pass

    def on_stop(self):
        """ Is invoked by the Stop command when method is stopped. """
        self._last_event = "stop"

    def on_engine_shutdown(self):
        """ Invoked once when engine shuts down"""
        pass

    # --- TagLifetime end ----

class EngineTestRunner:
    """ Expose the external interface to Engine to tests. """
    def __init__(self, engine_factory: EngineFactory, pcode: str = "", speed: float = 1.0) -> None:
        self.engine_factory = engine_factory
        self.pcode = pcode
        self.speed = speed

    @contextmanager
    def run(self) -> Generator[EngineTestInstance, None, None]:
        engine = self.engine_factory()
        instance = EngineTestInstance(engine, self.pcode, self.speed)
        try:
            yield instance
        except Exception:
            raise
        finally:
            engine.cleanup()


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

        time.sleep(0.1)
        engine.tick()


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


def configure_test_logger():
    logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')


def set_engine_debug_logging():
    engine_modules = [
        "openpectus.engine.engine",
        # "openpectus.engine.internal_commands",
        "openpectus.engine.internal_commands_impl",
    ]
    for m in engine_modules:
        logger = logging.getLogger(m)
        logger.setLevel(logging.DEBUG)


def set_interpreter_debug_logging():
    logger = logging.getLogger("openpectus.lang.exec.pinterpreter")
    logger.setLevel(logging.DEBUG)
