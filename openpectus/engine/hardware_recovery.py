from dataclasses import dataclass
from enum import Enum
import inspect
import logging
import time
from typing import Any, Callable, Sequence

from openpectus.engine.hardware import HardwareLayerBase, HardwareLayerException, Register, RegisterDirection
from openpectus.engine.models import ConnectionStatusEnum
from openpectus.lang.exec.tags import Tag


logger = logging.getLogger(__name__)


class ErrorRecoveryState(Enum):
    Disconnected = 0
    """ No connection attempt yet """
    OK = 1
    """ No problem with the hardware connection """
    Issue = 2
    """ There may be an issue. A few errors detected. Trying to recover by waiting for success reads/writes
    while masking errors."""
    Reconnect = 3
    """ There is a connection an issue. Trying to recover by reconnecting while still masking errors."""
    Error = 4
    """ Connection is lost and reconnection has not been successful. Trying to recover by reconnecting.
    Errors are no longer masked."""


@dataclass
class ErrorRecoveryConfig:
    reconnect_timeout_seconds = 10
    """ Number of seconds in state Issue before changing to state Reconnect """
    error_timeout_seconds = 5*60*60
    """ Number of seconds in state Reconnect before changing to state Error """


class ErrorRecoveryDecorator(HardwareLayerBase):
    """ Implements error recovery as a decorator around concrete hardware, without coupling it to Engine.

    Error recovery has the 5 states defined in `ErrorRecoveryState`. It is configured using the time thresholds
    defined in `ErrorRecoveryConfig`.

    Once connected, state is `OK`. This state is kept until a read or write error occurs (`read()`, `write()` or
    one of the batch variants raise `HardwareLayerException`). Such an error causes state to transition to `Issue`.
    In this state, if a success read/write occurs, state transitions back to `OK`. If no success read/write occurs
    within a duration of `issue_timeout_seconds`, state is set to `Reconnect`.

    In state `Reconnect`, reconnect attempts are started. If successful, state is set to `OK`. If not successful
    within a duration of `error_timeout_seconds`, state is set to `Error`.

    While in states `Issue` and `Reconnect`, any read and write errors are masked by returning last-known-good values for
    reads and caching values for writes. This means that the Engine (and the user) will not notice the connection loss.

    The one exception to this is uod commands. We have to assume that a uod command cannot execute correctly
    without hardware connection so we have to fail uod commands. (A possible improvement would be to require uod
    commands to consider the connection and fail with predefined exception types).

    In state `Error` reconnect attempts continue but errors are no longer masked. The  `Connection Status` tag is set to
    'Disconnected'. If reconnect is successful, state is set to `OK` and `Connection Status` is set to `Connected`.

    The consequence of no longer masking errors, is that the Engine will enter the "paused on error" state where the
    user can decide whether to continue or not.

    Note: It is unlikely but possible that errors occur so soon after successful connection that no value is yet available
    as last-known-good. In this case, a read returns a None value is returned and the error is logged.

    Reconnect note:
    The default implementation uses the tick() method to detect and execute reconnect. If this takes too long
    and hurts engine timing, the hardware should instead implement its reconnect via threading.
    """

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(state={self.state}, ' +
                f'last_success_read_write={self.last_success_read_write}, ' +
                f'last_success_connect={self.last_success_connect}, ' +
                f'last_state_reconnect_time={self.last_state_reconnect_time}, decorated={self.decorated})')

    def __init__(self, decorated: HardwareLayerBase, config: ErrorRecoveryConfig, connection_status_tag: Tag) -> None:
        super().__init__()
        self.decorated = decorated
        self.config = config
        self.connection_status_tag = connection_status_tag
        self.connect_error_callback: Callable[[Exception], None] | None = None
        self.error_callback: Callable[[], None] | None = None
        self.reconnect_callback: Callable[[], None] | None = None
        self.reconnecting_callback: Callable[[], None] | None = None
        self.reconnected_callback: Callable[[], None] | None = None

        self.last_known_good_reads: dict[str, Any] = {}
        self.pending_writes: dict[Register, Any] = {}

        self.state: ErrorRecoveryState = ErrorRecoveryState.Disconnected

        self.last_success_read_write = time.time()
        self.last_success_connect = time.time()
        self.last_state_reconnect_time = time.time()
        """ The time of the last transition to state Reconnect"""

        self.reconnect_count = 0
        self.reconnect_tick = -1
        # Hardcoded ticks for exponential backoff. Multiples of the largest value are implicitly included
        self.reconnect_backoff_ticks = [5, 20, 100, 300, 1200, 18000]

        # support initialization with connected hwl, which is the default case
        if decorated.is_connected:
            logger.debug("Initializing recovery with state OK from connected hardware")
            self.state = ErrorRecoveryState.OK
            self.on_ok()
        else:
            logger.debug("Initializing recovery from disconnected hardware")

        try:
            self._setup_decorated_method_forwards()
        except Exception:
            logger.error("Error setting up decorated hardware method forwards", exc_info=True)

    def get_recovery_state(self) -> ErrorRecoveryState:
        return self.state

    @property
    def is_connected(self) -> bool:
        """ Returns a value indicating whether there is an active connection to the hardware."""
        return self.state in [ErrorRecoveryState.OK, ErrorRecoveryState.Issue]

    @property
    def registers(self):
        return self.decorated.registers

    def success_read_write(self):
        now = time.time()
        logger.debug(f"RW success, state: {self.state}")
        self.last_success_read_write = now
        if self.state == ErrorRecoveryState.Issue:
            logger.debug(f"RW success, state transition: {ErrorRecoveryState.Issue} -> {ErrorRecoveryState.OK}")
            self.state = ErrorRecoveryState.OK
            self.on_ok()

    def error_read_write(self):
        now = time.time()
        logger.debug(f"RW error, state: {self.state}")
        if self.state == ErrorRecoveryState.OK:
            logger.debug(f"RW error, state transition: {ErrorRecoveryState.OK} -> {ErrorRecoveryState.Issue}")
            self.state = ErrorRecoveryState.Issue
            self.on_issue()
        elif self.state == ErrorRecoveryState.Issue:
            if self.last_success_read_write + self.config.reconnect_timeout_seconds < now:
                logger.debug(f"RW error, state transition: {ErrorRecoveryState.Issue} -> {ErrorRecoveryState.Reconnect}")
                self.state = ErrorRecoveryState.Reconnect
                self.on_reconnect()
        elif self.state == ErrorRecoveryState.Reconnect:
            if self.last_state_reconnect_time + self.config.error_timeout_seconds < now:
                logger.debug(f"RW error, state transition: {ErrorRecoveryState.Reconnect} -> {ErrorRecoveryState.Error}")
                self.state = ErrorRecoveryState.Error
                self.on_error()

    def _is_backoff_tick(self, tick: int) -> bool:
        if tick in self.reconnect_backoff_ticks:
            return True
        last = self.reconnect_backoff_ticks[-1]
        if tick > last and tick % last == 0:
            return True
        return False

    def tick(self):
        if self.state in [ErrorRecoveryState.Reconnect, ErrorRecoveryState.Error]:
            self.reconnect_tick += 1
            if self._is_backoff_tick(self.reconnect_tick):
                logger.info("Reconnecting")
                self.on_reconnecting()
                try:
                    self.reconnect()
                    self.reconnect_tick = -1
                    self.state = ErrorRecoveryState.OK
                    self.on_reconnected()
                except Exception:
                    logger.error("Reconnect failed", exc_info=True)

    def _update_connection_status(self):
        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Error]:
            value = ConnectionStatusEnum.Disconnected
        else:
            value = ConnectionStatusEnum.Connected
        logger.debug(f"Setting connection status to: {value} based on state: {self.state}")
        self.connection_status_tag.set_value(str(value), time.time())

    # Callbacks

    def on_ok(self):
        logger.debug("on_ok fired")
        self.decorated._is_connected = True
        self._update_connection_status()

    def on_issue(self):
        logger.debug("on_issue fired")
        self._update_connection_status()

    def on_error(self):
        logger.debug("on_error fired")
        self._update_connection_status()
        self.decorated._is_connected = False
        if self.error_callback is not None:
            self.error_callback()

    def on_reconnect(self):
        logger.debug("on_reconnect fired")
        self._update_connection_status()
        self.last_state_reconnect_time = time.time()

    def on_reconnecting(self):
        logger.debug("on_reconnecting fired")
        self._update_connection_status()
        if self.reconnecting_callback is not None:
            self.reconnecting_callback()

    def on_reconnected(self):
        logger.debug("on_reconnected fired")
        self._update_connection_status()
        self.decorated._is_connected = True
        if self.reconnected_callback is not None:
            self.reconnected_callback()

    # Decorator impl

    def read(self, r: Register) -> Any:
        if RegisterDirection.Read not in r.direction:
            raise KeyError(f"Cannot read from register {r.name} which has direction {r.direction}")

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Error]:
            raise HardwareLayerException(f"Cannot read in state {self.state}")

        if self.state == ErrorRecoveryState.Reconnect:
            # in this state we are reconnecting. we do not want a possible success read to interfere
            # with reconnection. But we do want a possible transition to Error so we note an error.
            self.error_read_write()
            if r.name in self.last_known_good_reads.keys():
                return self.last_known_good_reads[r.name]
            else:
                logger.error(f"No known good value available for read of register {r.name}")
                return None

        try:
            value = self.decorated.read(r)
            self.last_known_good_reads[r.name] = value
            self.success_read_write()
            return value
        except HardwareLayerException:
            self.error_read_write()
            return self._get_last_known_good_values([r])[0]

    def read_batch(self, registers: Sequence[Register]) -> list[Any]:
        for r in registers:
            if RegisterDirection.Read not in r.direction:
                raise KeyError(f"Cannot read from register {r.name} which has direction {r.direction}")

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Error]:
            raise HardwareLayerException(f"Cannot read in state {self.state}")

        if self.state == ErrorRecoveryState.Reconnect:
            self.error_read_write()
            return self._get_last_known_good_values(registers)

        try:
            values = self.decorated.read_batch(registers)
            for value, r in zip(values, registers):
                self.last_known_good_reads[r.name] = value
            self.success_read_write()
            return values
        except HardwareLayerException:
            self.error_read_write()
            return self._get_last_known_good_values(registers)

    def _get_last_known_good_values(self, registers: Sequence[Register]) -> list[Any]:
        values = []
        for r in registers:
            if r.name in self.last_known_good_reads.keys():
                values.append(self.last_known_good_reads[r.name])
            else:
                logger.error(f"Masked read failed. Register {r.name} did not have a last-known-good value")
                values.append(None)
        return values

    def write(self, value: Any, r: Register) -> None:
        if RegisterDirection.Write not in r.direction:
            raise KeyError(f"Cannot write to register {r.name} which has direction {r.direction}")

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Error]:
            raise HardwareLayerException(f"Cannot write in state {self.state}")

        if self.state == ErrorRecoveryState.Reconnect:
            self.error_read_write()
            self.pending_writes[r] = value
            return

        try:
            self.decorated.write(value, r)
            self.success_read_write()
            self._write_pending_values(except_names=[r.name])
        except HardwareLayerException:
            self.error_read_write()
            if self.state == ErrorRecoveryState.Error:
                return
            self.pending_writes[r] = value


    def write_batch(self, values: Sequence[Any], registers: Sequence[Register]):
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise KeyError(f"Cannot write to register {r.name} which has direction {r.direction}")

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Error]:
            raise HardwareLayerException(f"Cannot write in state {self.state}")

        if self.state == ErrorRecoveryState.Reconnect:
            self.error_read_write()
            for value, r in zip(values, registers):
                self.pending_writes[r] = value
            return

        try:
            self.decorated.write_batch(values, registers)
            self.success_read_write()
            self._write_pending_values(except_names=[r.name for r in registers])
        except HardwareLayerException:
            self.error_read_write()
            if self.state == ErrorRecoveryState.Error:
                return
            for value, r in zip(values, registers):
                self.pending_writes[r] = value

    def connect(self):
        try:
            self.decorated.connect()

            if self.state == ErrorRecoveryState.Disconnected:
                self.state = ErrorRecoveryState.OK
                self.on_ok()

            self.connection_state = ConnectionStatusEnum.Connected
            self.last_success_connect = time.time()
        except HardwareLayerException:
            logger.error("Decorated connect failed", exc_info=True)
            raise

    def disconnect(self):
        return self.decorated.disconnect()

    def _write_pending_values(self, except_names: list[str] = []):
        if self.state == ErrorRecoveryState.OK and len(self.pending_writes) > 0:
            pending_items = list(self.pending_writes.items())
            for register, value in pending_items:
                if register.name in except_names:
                    continue
                try:
                    self.decorated.write(value, register)
                    del self.pending_writes[register]
                except HardwareLayerException:
                    pass  # Better luck next time. We just had a success write so chances are good

    def _setup_decorated_method_forwards(self):
        """ Set up method forwards to avoid the decorator breaking commands that are implemented as methods
            on the concrete hardware
        """
        def callable_publics_predicate(member):
            if not inspect.ismethod(member) and not inspect.isfunction(member):
                return False
            if (name := getattr(member, "__name__", None)) is not None:
                if name.startswith("__"):
                    return False
            return True

        decorated_members = inspect.getmembers_static(self.decorated, callable_publics_predicate)
        self_member_names = [member[0] for member in inspect.getmembers_static(self, callable_publics_predicate)]
        for member in decorated_members:
            name: str = member[0]
            if name not in self_member_names:
                logger.info(f"Forwarding method {name} from hardware class {type(self.decorated).__name__} to decorator")
                func = member[1]

                # define local method that forwards calls to func using self.decorated as its self
                def caller(*args, **kvargs):
                    return func(self.decorated, *args, **kvargs)
                setattr(self, name, caller)
