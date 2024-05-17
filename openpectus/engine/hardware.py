from enum import Flag, auto
import logging
from typing import Any, Sequence


logger = logging.getLogger(__name__)


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
        self._options: dict[str, Any] = options

    @property
    def name(self):
        return self._name

    @property
    def direction(self) -> RegisterDirection:
        return self._direction

    @property
    def options(self) -> dict[str, Any]:
        return self._options

    def __str__(self):
        return f"Register(name={self._name})"

    def __repr__(self):
        return str(self)


class HardwareLayerException(Exception):
    """ Raised when hardware connection issues occur. """

    def __init__(self, message: str, ex: Exception | None = None) -> None:
        self.message = message
        self.ex = ex

    def __str__(self):
        return self.message


class HardwareLayerBase():
    """ Represents the hardware layer """
    def __init__(self) -> None:
        self.registers: dict[str, Register] = {}
        self._is_connected: bool = False

    def __enter__(self):
        """ Allow use as context manager. """
        self.connect()

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def tick(self):
        """ Invoked on each tick by engine. """
        pass

    @property
    def is_connected(self) -> bool:
        """ Returns a value indicating whether there is an active connection to the hardware."""
        return self._is_connected

    def read(self, r: Register) -> Any:
        if RegisterDirection.Read not in r.direction:
            raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        raise NotImplementedError

    def read_batch(self, registers: Sequence[Register]) -> list[Any]:
        """ Read batch of register values. Override to provide efficient implementation """
        for r in registers:
            if RegisterDirection.Read not in r.direction:
                raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        values = []
        for r in registers:
            values.append(self.read(r))
        return values

    def write(self, value: Any, r: Register) -> None:
        if RegisterDirection.Write not in r.direction:
            raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        raise NotImplementedError

    def write_batch(self, values: Sequence[Any], registers: Sequence[Register]):
        """ Write batch of register values. Override to provide efficient implementation """
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        for v, r in zip(values, registers):
            self.write(v, r)

    def connect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. Abstract method. """
        raise NotImplementedError()

    def disconnect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. Abstract method. """
        raise NotImplementedError()

    def reconnect(self):
        """ Perform a reconnect. The default implementation just disconnects (ignoring any error)
        and connects. Override to perform a more advanced reconnect, like using a thread.
        """
        logger.info("Reconnecting")
        try:
            logger.info("Reconnect - disconnect")
            self.disconnect()
        except Exception:
            logger.error("Reconnect - disconnect error", exc_info=True)
            # we continue - disconnect should not fail but even if it does,
            # connect might still work

        try:
            self.connect()
            logger.info("Reconnect complete")
        except Exception:
            logger.error("Reconnect - connect error", exc_info=True)
            raise HardwareLayerException("Reconnect attempt failed")


    def validate_offline(self):
        """ Perform checks that verify that the registers definition is valid. Raise on validation error. """
        pass

    def validate_online(self):
        """ Perform checks that verify that the register definition works. Raise on validation error. """
        pass


class NullHardware(HardwareLayerBase):
    """ Represents no hardware. Used by tests. """
    def __init__(self) -> None:
        super().__init__()
        self._is_connected = True

    def read(self, r: Register) -> Any:
        return None

    def write(self, value: Any, r: Register):
        pass
