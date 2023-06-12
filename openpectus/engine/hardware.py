from enum import Flag, auto
from typing import Any, Dict, Iterable, List


class RegisterDirection(Flag):
    Read = auto()
    Write = auto()
    Both = Read | Write


class Register():
    """ Represents a hardware register or named value. """
    def __init__(self, name: str, direction: RegisterDirection, **options) -> None:
        self._name: str = name
        self._direction: RegisterDirection = direction
        # self._value: Any = None
        self._options: Dict[str, Any] = options

    @property
    def name(self):
        return self._name

    @property
    def direction(self) -> RegisterDirection:
        return self._direction

    # @property
    # def value(self):
    #     return self._value

    # @value.setter
    # def value(self, val: Any):
    #     self._value = val

    @property
    def options(self):
        return self._options


class HardwareLayerException(Exception):
    """ Raised when hardware connection issues occur. """

    def __init__(self, message: str, ex: Exception | None = None) -> None:
        self.message = message
        self.ex = ex

    def __str__(self):
        return self.message


# TODO use better type than Any for hw values

class HardwareLayerBase():
    """ Represents the hardware layer, typically implemented via OPCUA"""
    def __init__(self) -> None:
        self.registers: Dict[str, Register] = {}

    def read(self, r: Register) -> Any:
        raise NotImplementedError()

    def read_batch(self, registers: list[Register]) -> list[Any]:
        """ Read batch of register values. Override to provide efficient implementation """
        values = []
        for r in registers:
            if RegisterDirection.Read in r.direction:
                values.append(self.read(r))
        return values

    def write(self, value: Any, r: Register):
        if RegisterDirection.Write not in r.direction:
            pass
        raise NotImplementedError()

    def write_batch(self, values: Iterable[Any], registers: Iterable[Register]):
        """ Write batch of register values. Override to provide efficient implementation """
        for v, r in zip(values, registers):
            if RegisterDirection.Write in r.direction:
                self.write(v, r)

    def connect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        pass

    def disconnect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        pass
