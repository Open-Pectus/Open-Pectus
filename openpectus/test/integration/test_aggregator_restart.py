import asyncio
import atexit
import logging
import os
import time
import urllib.parse
import unittest
import tempfile
import sys
import subprocess
import signal
import shutil
from typing import Any

from pydantic import TypeAdapter
import httpx

import openpectus.aggregator.main
import openpectus.engine.configuration.demo_uod
from openpectus.aggregator.routers.dto import (
    ProcessUnit,
    ExecutableCommand,
    CommandSource,
    ProcessUnitStateEnum,
    Method,
    MethodLine,
    PlotLog,
)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


def get_process_units(port) -> list[ProcessUnit]:
    process_list_adapter = TypeAdapter(list[ProcessUnit])
    response = httpx.get(f"http://127.0.0.1:{port}/api/process_units")
    return process_list_adapter.validate_json(response.text)

def execute_command_on_process_unit(port, command_name: str, process_unit: ProcessUnit):
    command = ExecutableCommand(
        command=command_name,
        source=CommandSource.UNIT_BUTTON
    )
    url = f"http://127.0.0.1:{port}/api/process_unit/{urllib.parse.quote(process_unit.id)}/execute_command"
    httpx.post(url, json=command.model_dump(), timeout=5)

def method_from_text(method_text: str):
    return Method(
        lines=[MethodLine(id=str(i), content=content) for i, content in enumerate(method_text.splitlines())],
        version=0,
        last_author="TEST"
    )

def set_method_on_process_unit(port, method: Method, process_unit: ProcessUnit):
    url = f"http://127.0.0.1:{port}/api/process_unit/{urllib.parse.quote(process_unit.id)}/method"
    httpx.post(url, json=method.model_dump(), timeout=5)

def get_method_on_process_unit(port, process_unit: ProcessUnit):
    url = f"http://127.0.0.1:{port}/api/process_unit/{urllib.parse.quote(process_unit.id)}/method"
    return Method.model_validate(httpx.get(url, timeout=5).json())

def get_plot_log_on_process_unit(port, process_unit: ProcessUnit):
    url = f"http://127.0.0.1:{port}/api/process_unit/{urllib.parse.quote(process_unit.id)}/plot_log"
    return PlotLog.model_validate(httpx.get(url, timeout=5).json())

def tick_times_from_plotlog(plot_log: PlotLog) -> set[float]:
    tick_times = set()
    for entry in plot_log.entries.values():
        for value in entry.values:
            tick_times.add(value.tick_time)
    return tick_times


class ConsoleAppRunner:
    def __init__(self, program: str, args: list[str]) -> None:
        self.program = program
        tempfile.mktemp()
        self.logfile_name = tempfile.NamedTemporaryFile(suffix=".log").name
        logger.debug(f"Using temp file {self.logfile_name}")
        self.process: subprocess.Popen[Any] | None = None
        self.final_output = ""
        self.args = args
        self.lines: list[str] = []

    def start(self):
        self.final_output = ""
        self.logfile = open(self.logfile_name, "wb")
        args = [self.program] + self.args
        self.process = subprocess.Popen(
            args,
            stdout=self.logfile,
            stderr=subprocess.STDOUT,
            encoding="utf-8"
        )
        atexit.register(self.stop)

    def stop(self):
        atexit.unregister(self.stop)
        if self.process:
            logger.debug("Killing process")
            if sys.platform.lower() == "linux":
                # It's possible to send CTRL-C on linux
                self.process.send_signal(signal.SIGINT)
                self.process.wait()
            else:
                # Kill is the only option for Windows
                self.process.kill()
                self.process.wait()
            with open(self.logfile_name, "r") as f:
                self.final_output = f.read()
        try:
            self.logfile.close()
        except Exception:
            logger.error("Failed to close file")
        if os.path.exists(self.logfile_name):
            time.sleep(0.1)
            os.unlink(self.logfile_name)

    @property
    def output(self) -> str:
        if self.final_output:
            return self.final_output
        for i in range(5):
            try:
                with open(self.logfile_name, "r") as reader:
                    return reader.read()
            except PermissionError:
                # This error occours when reading is performed while the file is being flushed to disk.
                # Just try again later.
                time.sleep(0.05)
        raise Exception("Unable to read {self.logfile_name}.")


class TestUsingConsoleAppRunner(unittest.TestCase):
    def assertHasOutput(self, runner: ConsoleAppRunner, expected_text: str, timeout_secs=5):
        output = runner.output
        if expected_text in output:
            return
        end_time = time.time() + timeout_secs
        while time.time() < end_time:
            output = runner.output
            if expected_text in output:
                return
            time.sleep(0.5)

        raise AssertionError(f"Expected text '{expected_text}' was not found in output",
                             f"Output is: {output}")


class TestAggregatorRestart(TestUsingConsoleAppRunner):
    @unittest.skipUnless(sys.platform.lower() == "linux", "This test cannot run correctly on Windows.")
    def test_reconnect_single_engine(self, port: int = 8718):
        temporary_sqlite_db_filename = tempfile.NamedTemporaryFile(suffix=".sqlite3").name

        method = method_from_text("\n".join([
            "Mark: A",
            "Wait: 10 s",
            "Mark: B",
            "Wait: 10 s",
            "Mark: C",
            "Wait: 10 s",
        ]))

        # Start aggregator via python (not via command script) to enable py-spy profiling
        aggregator = ConsoleAppRunner(
            "python",
            [
                openpectus.aggregator.main.__file__,
                "--port",
                str(port),
                "--database",
                temporary_sqlite_db_filename,
            ]
        )
        logger.debug("Starting aggregator")
        aggregator.start()
        self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")
        logger.debug(f"Aggregator started http://127.0.0.1:{port}")

        # Create Open Pectus Engine
        engine = ConsoleAppRunner(
            "pectus-engine",
            [
                "--aggregator_port",
                str(port),
                "--uod",
                openpectus.engine.configuration.demo_uod.__file__,
            ]
        )

        # Start engine and wait for it to be ready
        logger.debug("Starting engine")
        engine.start()
        self.assertHasOutput(engine, "Starting engine on first steady-state")
        logger.debug("Engine ready for run to start")

        # Check process unit is ready
        process_units = get_process_units(port)
        assert len(process_units) == 1
        process_unit = process_units[0]
        self.assertEqual(process_unit.state.state, ProcessUnitStateEnum.READY)

        # Set method
        logger.debug("Setting method")
        set_method_on_process_unit(port, method, process_unit)
        self.assertHasOutput(engine, "Incomming set_method command from aggregator")

        # Start run
        logger.debug("Starting run")
        execute_command_on_process_unit(port, "Start", process_unit)
        self.assertHasOutput(engine, "Archiver started")
        logger.debug("Runs started")
        time.sleep(10)

        # Get plotlog before stopping aggregator
        plot_log_before_stop = get_plot_log_on_process_unit(port, process_unit)

        # Stop aggregator for a while so all engines lose connection
        logger.debug("Stopping aggregator for a while")
        aggregator.stop()
        self.assertHasOutput(engine, "Changing state: Failed -> Disconnected", 10)
        logger.debug("Engine lost connection to aggregator")

        time.sleep(10)

        # Start aggregator again and wait for all engines to reconnect
        logger.debug("Starting aggregator again")
        aggregator.start()
        self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")
        logger.debug("Aggregator started again")
        self.assertHasOutput(engine, "Changing state: CatchingUp -> Reconnected", 15)
        logger.debug("Engine reconnected")
        aggregator_method = get_method_on_process_unit(port, process_unit)

        # Check that aggregator knows of the method on the engine
        for a, b in zip(aggregator_method.lines, method.lines):
            self.assertEqual(a.id, b.id)
            self.assertEqual(a.content, b.content)

        # Check that plot log after restart has all the points from
        # before the restart and that it is larger.
        plot_log_after_aggregator_restart = get_plot_log_on_process_unit(port, process_unit)
        self.assertTrue(
            tick_times_from_plotlog(plot_log_before_stop).issubset(
                tick_times_from_plotlog(plot_log_after_aggregator_restart)
            )
        )
        self.assertGreater(
            len(tick_times_from_plotlog(plot_log_after_aggregator_restart)),
            len(tick_times_from_plotlog(plot_log_before_stop))
        )

        # Stop run
        logger.debug("Stopping run")
        execute_command_on_process_unit(port, "Stop", process_unit)
        self.assertHasOutput(engine, "Stopped", 30)
        logger.debug("Engines stopped run")
        engine.stop()
        aggregator.stop()
    
    @unittest.skipIf(bool(os.environ.get("OPENPECTUS_INTEGRATION_SKIP_SLOW_TESTS")), reason="Skipping slow tests as configured")
    @unittest.skipUnless(sys.platform.lower() == "linux", "This test cannot run correctly on Windows.")
    def test_reconnect_single_heavy_engine(self, port: int = 8719):
        temporary_sqlite_db_filename = tempfile.NamedTemporaryFile(suffix=".sqlite3").name

        # Start aggregator via python (not via command script) to enable py-spy profiling
        aggregator = ConsoleAppRunner(
            "python",
            [
                openpectus.aggregator.main.__file__,
                "--port",
                str(port),
                "--database",
                temporary_sqlite_db_filename,
            ]
        )
        logger.debug("Starting aggregator")
        aggregator.start()
        self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")
        logger.debug(f"Aggregator started http://127.0.0.1:{port}")

        # Create Open Pectus Engine
        engine = ConsoleAppRunner(
            "pectus-engine",
            [
                "--aggregator_port",
                str(port),
                "--uod",
                os.path.join(os.path.dirname(__file__), "heavy_uod.py"),
            ]
        )

        # Start engine and wait for it to be ready
        logger.debug("Starting engine")
        engine.start()
        self.assertHasOutput(engine, "Starting engine on first steady-state")
        logger.debug("Engine ready for run to start")

        # Check process unit is ready
        process_units = get_process_units(port)
        assert len(process_units) == 1
        process_unit = process_units[0]
        self.assertEqual(process_unit.state.state, ProcessUnitStateEnum.READY)

        # Start run
        logger.debug("Starting run")
        execute_command_on_process_unit(port, "Start", process_unit)
        self.assertHasOutput(engine, "Archiver started")
        logger.debug("Runs started")
        time.sleep(10)

        # Get plotlog before stopping aggregator
        plot_log_before_stop = get_plot_log_on_process_unit(port, process_unit)

        # Stop aggregator for a while so all engines lose connection
        logger.debug("Stopping aggregator for a while")
        aggregator.stop()
        self.assertHasOutput(engine, "Changing state: Failed -> Disconnected", 10)
        logger.debug("Engine lost connection to aggregator")

        time.sleep(10)

        # Start aggregator again and wait for all engines to reconnect
        logger.debug("Starting aggregator again")
        aggregator.start()
        self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")
        logger.debug("Aggregator started again")
        self.assertHasOutput(engine, "Changing state: CatchingUp -> Reconnected", 15)
        logger.debug("Engine reconnected")

        # Check that plot log after restart has all the points from
        # before the restart and that it is larger.
        plot_log_after_aggregator_restart = get_plot_log_on_process_unit(port, process_unit)
        self.assertTrue(
            tick_times_from_plotlog(plot_log_before_stop).issubset(
                tick_times_from_plotlog(plot_log_after_aggregator_restart)
            )
        )
        self.assertGreater(
            len(tick_times_from_plotlog(plot_log_after_aggregator_restart)),
            len(tick_times_from_plotlog(plot_log_before_stop))
        )

        # Stop run
        logger.debug("Stopping run")
        execute_command_on_process_unit(port, "Stop", process_unit)
        self.assertHasOutput(engine, "Stopped", 30)
        logger.debug("Engines stopped run")
        engine.stop()
        aggregator.stop()

    @unittest.skipIf(bool(os.environ.get("OPENPECTUS_INTEGRATION_SKIP_SLOW_TESTS")), reason="Skipping slow tests as configured")
    @unittest.skipUnless(sys.platform.lower() == "linux", "This test cannot run correctly on Windows.")
    def test_reconnect_multiple_engines(self, port: int = 8720, n_engines=5):
        temporary_sqlite_db_filename = tempfile.NamedTemporaryFile(suffix=".sqlite3").name
        atexit.register(lambda: os.unlink(temporary_sqlite_db_filename))

        # Start aggregator via python (not via command script) to enable py-spy profiling
        aggregator = ConsoleAppRunner(
            "python",
            [
                openpectus.aggregator.main.__file__,
                "--port",
                str(port),
                "--database",
                temporary_sqlite_db_filename
            ]
        )
        logger.debug("Starting aggregator")
        aggregator.start()
        self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")
        logger.info(f"Aggregator started http://127.0.0.1:{port}")

        # Check if py-spy is available
        if shutil.which("py-spy"):  # pip install py-spy
            assert aggregator.process
            logger.info("Run the following command to profile using py-spy")
            command = [
                "py-spy",
                "record",
                "-o",
                f'"{os.path.join(os.path.dirname(__file__), "output.svg")}"',
                "-p",str(aggregator.process.pid),
            ]
            logger.info(" ".join(command))
            time.sleep(10)

        # Get "demo_uod.py" code
        with open(openpectus.engine.configuration.demo_uod.__file__, "r") as base_uod_file:
            base_uod_contents = base_uod_file.read()

        # Create n_engines Open Pectus Engines
        # The demo_uod is used as a template where the engine name is adjusted to be unique for each engine
        engines: list[ConsoleAppRunner] = []
        for i in range(n_engines):
            temp_uod_filename = tempfile.NamedTemporaryFile(suffix=".py").name
            with open(temp_uod_filename, "w") as temp_uod_file:
                temp_uod_file.write(base_uod_contents.replace("DemoUod", f"DemoUod {i}"))
                engines.append(ConsoleAppRunner(
                    "pectus-engine",
                    [
                        "--aggregator_port",
                        str(port),
                        "--uod",
                        temp_uod_filename
                    ]
                ))

        # Start engines and wait for them to be ready
        logger.info("Starting engines")
        [engine.start() for engine in engines]
        [self.assertHasOutput(engine, "Starting engine on first steady-state") for engine in engines]
        logger.info("All engines ready for runs to start")

        # Check all process units are ready
        process_units = get_process_units(port)
        assert len(process_units) == n_engines
        assert all(process_unit.state.state == ProcessUnitStateEnum.READY for process_unit in process_units)

        # Start runs on all engines simultaneously
        async def execute_command_on_process_units(command_name: str, process_units: list[ProcessUnit]):
            async with httpx.AsyncClient() as client:
                # Start runs on all engines
                command = ExecutableCommand(command=command_name, source=CommandSource.UNIT_BUTTON)
                responses = []
                for process_unit in process_units:
                    url = f"http://127.0.0.1:{port}/api/process_unit/{urllib.parse.quote(process_unit.id)}/execute_command"
                    responses.append(client.post(url, json=command.model_dump(), timeout=10))
                await asyncio.gather(*responses)
        logger.info("Starting runs")
        asyncio.run(execute_command_on_process_units("Start", process_units))
        [self.assertHasOutput(engine, "Archiver started") for engine in engines]
        logger.info("Runs started")
        time.sleep(10)

        # Stop aggregator for a while so all engines loose connection
        logger.info("Stopping aggregator for a while")
        aggregator.stop()
        [self.assertHasOutput(engine, "Changing state: Failed -> Disconnected") for engine in engines]
        logger.info("All engines lost connection to aggregator")

        time.sleep(10)

        # Start aggregator again and wait for all engines to reconnect
        logger.info("Starting aggregator again")
        aggregator.start()
        self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")
        logger.info("Aggregator started again")
        [self.assertHasOutput(engine, "Changing state: CatchingUp -> Reconnected", 20) for engine in engines]
        logger.info("All engines reconnected")

        # Stop runs on all engines
        logger.info("Stopping runs on all engines")
        asyncio.run(execute_command_on_process_units("Stop", process_units))
        [self.assertHasOutput(engine, "Stopped") for engine in engines]
        logger.info("All engines stopped their runs")
        [engine.stop() for engine in engines]
        aggregator.stop()