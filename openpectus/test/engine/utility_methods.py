import time
from openpectus.engine.models import EngineCommandEnum

import openpectus.protocol.models as Mdl
from openpectus.engine.engine import Engine
from openpectus.lang.grammar.pgrammar import PGrammar
from openpectus.lang.model.pprogram import PProgram


def build_program(s) -> PProgram:
    p = PGrammar()
    p.parse(s)
    return p.build_model()


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

        time.sleep(0.1)
        engine.tick()
