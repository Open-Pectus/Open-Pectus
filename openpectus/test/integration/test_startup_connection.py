import logging
import os
from subprocess import Popen, STDOUT
import time
from typing import Any
import unittest
import tempfile

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ConsoleAppRunner():
    def __init__(self, program: str, args: list[str]) -> None:
        self.program = program
        tempfile.mktemp()
        self.logfile_name = tempfile.NamedTemporaryFile(suffix=".log").name
        logger.debug(f"Using temp file {self.logfile_name}")
        self.process: Popen[Any] | None = None
        self.args = args
        self.lines: list[str] = []

    def __enter__(self):
        return self

    def start(self):
        self.logfile = open(self.logfile_name, "wb")
        args = [self.program] + self.args
        self.process = Popen(args, stdout=self.logfile, stderr=STDOUT, encoding="utf-8")

    @property
    def output(self) -> str:
        for i in range(5):
            try:
                with open(self.logfile_name, "r") as reader:
                    return reader.read()
            except PermissionError:
                # This error occours when reading is performed while the file is being flushed to disk.
                # Just try again later.
                time.sleep(0.05)
        raise Exception("Unable to read {self.logfile_name}.")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.process:
            logger.debug("Killing process")
            self.process.kill()
        try:
            self.logfile.close()
        except Exception:
            logger.error("Failed to close file")
        if os.path.exists(self.logfile_name):
            time.sleep(1)
            os.unlink(self.logfile_name)


def get_demo_uod_path() -> str:
    uod_file_path = os.path.join(
        os.path.dirname(  # openpectus
            os.path.dirname(  # openpectus/test
                os.path.dirname(__file__)  # openpectus/test/engine
            )
        ),
        'engine',  # openpectus/engine
        'configuration',  # openpectus/engine/configuration
        'demo_uod.py',  # openpectus/engine/configuration/demo_uod.py
    )
    return uod_file_path

class TestStartupConnection(unittest.TestCase):

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

    def test_engine_can_connect_to_running_aggregator(self):
        port = "8727"
        with ConsoleAppRunner("pectus-aggregator", ["--port", port]) as aggregator, \
             ConsoleAppRunner("pectus-engine", ["--aggregator_port", port, "--uod", get_demo_uod_path()]) as engine:

            aggregator.start()
            self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")

            engine.start()
            self.assertHasOutput(engine, "Registering for engine id")

            self.assertHasOutput(aggregator, "Engine connected", 3)
            self.assertHasOutput(engine, "Changing state: Started -> Connected", 3)
            self.assertHasOutput(engine, "Starting engine on first steady-state", 3)


    def test_engine_can_connect_to_aggregator_started_after_engine(self):
        port = "8728"
        with ConsoleAppRunner("pectus-aggregator", ["--port", port]) as aggregator, \
             ConsoleAppRunner("pectus-engine", ["--aggregator_port", port, "--uod", get_demo_uod_path()]) as engine:

            engine.start()
            time.sleep(5)
            self.assertHasOutput(engine, "Registering for engine id")

            aggregator.start()
            time.sleep(5)
            self.assertHasOutput(aggregator, "Starting Open Pectus Aggregator")

            time.sleep(2)
            self.assertHasOutput(aggregator, "Engine connected")
            self.assertHasOutput(engine, "Changing state: CatchingUp -> Reconnected")
            self.assertHasOutput(engine, "Starting engine on first steady-state")
