import logging
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
    records = e.interpreter.runtimeinfo.records
    print("Runtime records: ", description)
    print("line | start | end   | name                 | states")
    print("-----|-------|-------|----------------------|-------------------")
    for r in records:
        name = f"{str(r.name):<20}" if r.name is not None else f"{str(r.node):<20}"
        line = f"{int(r.node.line):4d}" if r.node.line is not None else "   -"
        states = ", ".join([f"{st.state_name}: {st.state_tick}" for st in r.states])
        end = f"{r.visit_end_tick:5d}" if r.visit_end_tick != -1 else "    -"
        print(f"{line}   {r.visit_start_tick:5d}   {end}   {name}   {states}")
    print("-----|-------|-------|----------------------|-------------------")


def configure_test_logger():
    logging.basicConfig(format=' %(name)s :: %(levelname)-8s :: %(message)s')


def set_engine_debug_logging():
    engine_modules = ["openpectus.engine.engine",
                      "openpectus.engine.internal_commands",
                      "openpectus.engine.internal_commands_impl"]
    for m in engine_modules:
        logger = logging.getLogger(m)
        logger.setLevel(logging.DEBUG)


def set_interpreter_debug_logging():
    logger = logging.getLogger("openpectus.lang.exec.pinterpreter")
    logger.setLevel(logging.DEBUG)
