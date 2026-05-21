import time
from typing import Any, override

from openpectus.engine.hardware import HardwareLayerBase, Register
from openpectus.lang.exec.tags import Tag, TagDirection


class TestHW(HardwareLayerBase):
    __test__ = False

    def __init__(self, connected: bool = False) -> None:
        super().__init__()
        self.register_values = {}
        self._is_connected = connected

    @override
    def read(self, r: Register) -> Any:
        if r.name in self.registers.keys() and r.name in self.register_values.keys():
            return self.register_values[r.name]
        return None

    @override
    def write(self, value: Any, r: Register):
        if r.name in self.registers.keys():
            self.register_values[r.name] = value

    @override
    def connect(self):
        self._is_connected = True

    @override
    def disconnect(self):
        self._is_connected = False


class CalculatedLinearTag(Tag):
    """ Test tag that is used to simulate a value that is a linear function of time. """
    def __init__(self, name: str, unit: str | None, slope: float = 1.0) -> None:
        super().__init__(name, value=0.0, unit=unit, direction=TagDirection.NA)
        self.slope = slope

    def on_start(self, run_id: str):
        self.value = time.time() * self.slope

    def on_tick(self, tick_time: float, increment_time: float):
        self.value = time.time() * self.slope
