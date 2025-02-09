from enum import Flag, auto
import logging
from typing import Any, Sequence


logger = logging.getLogger(__name__)


class RegisterDirection(Flag):
    Read = auto()
    Write = auto()
    Both = Read | Write


class Register:
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

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}", direction={self.direction})'

    def __repr__(self):
        return str(self)


class HardwareLayerException(Exception):
    """ Raised when hardware connection issues occur. """

    def __init__(self, message: str, ex: Exception | None = None) -> None:
        self.message = message
        self.ex = ex

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(message="{self.message}")'


class HardwareLayerBase:
    """ Base class for hardware layer implementations. """
    def __init__(self) -> None:
        self._registers: dict[str, Register] = {}
        self._is_connected: bool = False

    def __enter__(self):
        """ Allow use as context manager. """
        self.connect()

    def __exit__(self, type, value, traceback):
        self.disconnect()

    def tick(self):
        """ Invoked on each tick by engine. """
        pass

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(is_connected={self.is_connected})'

    @property
    def registers(self) -> dict[str, Register]:
        return self._registers

    @property
    def is_connected(self) -> bool:
        """ Returns a value indicating whether there is an active connection to the hardware. Virtual property. """
        return self._is_connected

    def read(self, r: Register) -> Any:
        """ Read single register value. Abstract method. """
        if RegisterDirection.Read not in r.direction:
            raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        raise NotImplementedError

    def read_batch(self, registers: Sequence[Register]) -> list[Any]:
        """ Read batch of register values. Override to provide efficient implementation. Virtual method. """
        for r in registers:
            if RegisterDirection.Read not in r.direction:
                raise HardwareLayerException(f"Attempt to read unreadable register {r}.")
        values = []
        for r in registers:
            values.append(self.read(r))
        return values

    def write(self, value: Any, r: Register) -> None:
        """ Write single register value. Abstract method. """
        if RegisterDirection.Write not in r.direction:
            raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        raise NotImplementedError

    def write_batch(self, values: Sequence[Any], registers: Sequence[Register]):
        """ Write batch of register values. Override to provide efficient implementation. Virtual method. """
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise HardwareLayerException(f"Attempt to write unwritable register {r}.")
        for v, r in zip(values, registers):
            self.write(v, r)

    def connect(self):
        """ Connect to hardware. Throw HardwareLayerException on error. Virtual method.
        Implementations must call base method on completed connect.
        """
        self._is_connected = True

    def disconnect(self):
        """ Disconnect from hardware. Throw HardwareLayerException on error. Virtual method.
        Implementations must call base method on completed disconnect.
        """
        self._is_connected = False

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
        """ Perform checks that verify that the registers definition is valid. Raise on validation error. Virtual method. """
        pass

    def validate_online(self):
        """ Perform checks that verify online hardware access. Raise on validation error. Virtual method.

        The default implementation checks that all Read registers can be read. Override to add additional
        checks.
        """
        for r in self.registers.values():
            if RegisterDirection.Read in r.direction:
                _ = self.read(r)

    def show_online_register_details(self):
        """ Displays online register details to use in uod definition. """
        print("----- Register details -----")
        for r in self.registers.values():
            print(r)
            if RegisterDirection.Read in r.direction:
                try:
                    val = self.read(r)
                    print("Read successful")
                    print(f"Raw value read: '{val}', raw value type: {type(val)}")
                    if "to_tag" in r.options:
                        print("Register has 'to_tag' option defined")
                        try:
                            val = r.options["to_tag"](val)
                            print(f"'to_tag' value: '{val}', 'to_tag' value type: {type(val)}")
                        except Exception as ex:
                            print(f"Exception was raised trying to evaluate the to_tag option function: {ex}")
                except Exception:
                    logger.debug(f"Read of register '{r.name}' failed")
                    logger.error("Read exception", exc_info=True)
                print("")
        print("----------")


class NullHardware(HardwareLayerBase):
    """ Represents no hardware. Used by tests. """
    def __init__(self) -> None:
        super().__init__()
        self._is_connected = True

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'

    def read(self, r: Register) -> Any:
        return None

    def write(self, value: Any, r: Register):
        pass

    # override calls we don't know to not fail
    def __getattribute__(self, name: str) -> Any:
        def null_call():
            pass

        if not name.startswith("_") and not hasattr(super(), name):
            # print("name", name)
            return null_call
        return super().__getattribute__(name)
