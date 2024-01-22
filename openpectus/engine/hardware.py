from enum import Flag, auto
from typing import Any, Dict, Iterable
from datetime import datetime


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
        if RegisterDirection.Write in self._direction and 'safe_value' not in self._options:
            raise Exception(f"'safe_value' must be defined for writable register {self}.")

    @property
    def name(self):
        return self._name

    @property
    def direction(self) -> RegisterDirection:
        return self._direction

    @property
    def safe_value(self) -> Any:
        return self._options["safe_value"]

    # @property
    # def value(self):
    #     return self._value

    # @value.setter
    # def value(self, val: Any):
    #     self._value = val

    @property
    def options(self) -> Dict[str, Any]:
        return self._options

    def __str__(self):
        return f"Register(name={self._name})"


class HardwareLayerException(Exception):
    """ Raised when hardware connection issues occur. """

    def __init__(self, message: str, ex: Exception | None = None) -> None:
        self.message = message
        self.ex = ex

    def __str__(self):
        return self.message


class HardwareConnectionStatus():
    """ Represents the hardware connection status. """
    def __init__(self):
        self.is_connected: bool = False
        self.connection_attempt_time = None
        self.successful_connection_time = None

    def set_ok(self):
        self.is_connected = True
        self.successful_connection_time = datetime.now()

    def set_not_ok(self):
        self.is_connected = False

    def register_connection_attempt(self):
        self.connection_attempt_time = datetime.now()

    @property
    def status(self):
        return self.is_connected

# TODO use better type than Any for hw values


class HardwareLayerBase():
    """ Represents the hardware layer """
    def __init__(self) -> None:
        self.registers: Dict[str, Register] = {}
        self.connection_status: HardwareConnectionStatus = HardwareConnectionStatus()

    def __enter__(self):
        """ Allow use as context manager. """
        self.connect()

    def __exit__(self, type, value, traceback):
        self.disconnect()

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
        self.connection_status.register_connection_attempt()

    def disconnect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. """
        self.connection_status.set_not_ok()


class NullHardware(HardwareLayerBase):
    """ Represents no hardware. Used by tests. """
    def __init__(self) -> None:
        super().__init__()

    def read(self, r: Register) -> Any:
        return None

    def write(self, value: Any, r: Register):
        pass
