from dataclasses import dataclass
from enum import Enum
import logging
import time
from typing import Any, Callable, Sequence

from openpectus.engine.hardware import HardwareLayerBase, HardwareLayerException, Register, RegisterDirection
from openpectus.engine.models import ConnectionStatusEnum


logger = logging.getLogger(__name__)


class ErrorRecoveryState(Enum):
    Disconnected = 0
    """ No connection attempt yet """
    OK = 1
    """ No problem with hardware connection """
    Issue = 2
    """ There may be an issue. A few errors detected. Trying to recover by waiting for success reades or writes"""
    Error = 3
    """ Connection is considered lost because of persistent errors. Trying to recover by reconnecting. """
    Failure = 4
    """ Hardware connection has failed. Too many errors encountered, recovery not possible """


@dataclass
class ErrorRecoveryConfig():
    error_timeout_seconds = 10
    """ Number of seconds in state Issue before changing to state Error """
    fail_timeout_seconds = 120
    """ Number of seconds since state Issue before changing to state Failure """


class ErrorRecoveryDecorator(HardwareLayerBase):
    """ Implements error recovery as a decorator around concrete hardware, uncoupling it from Engine.

    Error recovery has the 5 states defined in `ErrorRecoveryState`. It is configured using the time thresholds
    defined in `ErrorRecoveryConfig`.

    Once connected, state is `OK`. This state is kept until read or write errors occur (`read()` or `write()`
    raises `HardwareLayerException`), which causes state to transition to `Issue`. In this state, if a success read/write
    occurs, state transitions back to `OK`. If no success read/write occurs before `error_timeout_seconds`
    passes, state is set to `Error`.

    While in states `Issue` and `Error`, any read and write errors are masked by returning last-known-good values for reads
    and caching values for writes.

    In state `Error`, the connection is considered lost and reconnects are attempted. If successful, state is set to `OK`.
    If not successful before `fail_timeout_seconds` passes, the connection is considered unrecoverable and state is
    set to `Failure`.

    In the `Failure` state, all reads and writes fail, which the Engine should consider an error and terminate
    any method running.


    How to restart to leave the Failure state? Do we have to restart the engine? That's not great.

    TODO
    Should probably replace HardwareConnectionStatus
    Child classes already signal errors to HardwareConnectionStatus like this

        except ConnectionError:
            self.connection_status.set_not_ok()
            raise HardwareLayerException(f"Not connected to {self.host}")
        except asyncua.sync.ThreadLoopNotRunning:
            raise HardwareLayerException("OPC-UA client is closed.")

    Reconnect:
    - when can we try this? Is it ok within the read or write cycles? Let's assume this until we know otherwise
    - can we do this automatically? looks that way. engine._run() calls connect(). We should just call this start instead
        and have decorator do this
        
    TODO : Engine now has to support hardware in disconnected state. So rules must be implemented in Engine;
        - don't allow method start if hw is disconnected
        - while running, check error recovery state and stop the run if state is Failure.
          - maybe dont check this directly but maybe just handle exception in read/write. When using decorator
            there exceptions should only occur in state Failure in which it is fine to stop any current run.
    TODO remove connection_status from hwl, including calls
            self.connection_status.set_not_ok()
            self.connection_status.set_ok()
            self.connection_status.register_connection_attempt()
        in concrete hwls
    """

    def __str__(self) -> str:
        return f"ErrorRecoveryDecorator(state={self.state},decoratee={type(self.decorated).__name__})"


    def __init__(
            self,
            decorated: HardwareLayerBase,
            config: ErrorRecoveryConfig,
            connect_error_callback: Callable[[Exception], None],
            error_callback:  Callable[[], None],
            fail_callback:  Callable[[], None],
            ) -> None:
        super().__init__()
        self.decorated = decorated
        self.config = config
        self.connect_error_callback = connect_error_callback
        self.error_callback = error_callback
        self.fail_callback = fail_callback

        self.last_known_good_reads: dict[str, Any] = {}
        self.pending_writes: dict[Register, Any] = {}

        self.state: ErrorRecoveryState = ErrorRecoveryState.Disconnected
        self.method_state_error: bool = False

        self.last_success_read_write = time.time()
        self.last_success_connect = time.time()

    def get_recovery_state(self) -> ErrorRecoveryState:
        return self.state

    def get_method_state_error(self) -> bool:
        return self.method_state_error

    def get_connection_state(self) -> ConnectionStatusEnum:
        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Failure]:
            return ConnectionStatusEnum.Disconnected
        return ConnectionStatusEnum.Connected

    def success_read_write(self):
        now = time.time()
        logger.debug(f"RW success, state: {self.state}")
        self.last_success_read_write = now
        if self.state == ErrorRecoveryState.Issue:
            logger.debug(f"RW success, state transition: {ErrorRecoveryState.Issue} -> {ErrorRecoveryState.OK}")
            self.state = ErrorRecoveryState.OK

    def error_read_write(self):
        now = time.time()
        logger.debug(f"RW error, state: {self.state}")
        if self.state == ErrorRecoveryState.OK:
            logger.debug(f"RW error, state transition: {ErrorRecoveryState.OK} -> {ErrorRecoveryState.Issue}")
            self.state = ErrorRecoveryState.Issue
        elif self.state == ErrorRecoveryState.Issue:
            if self.last_success_read_write + self.config.error_timeout_seconds < now:
                logger.debug(f"RW error, state transition: {ErrorRecoveryState.Issue} -> {ErrorRecoveryState.Error}")
                self.state = ErrorRecoveryState.Error
                self.on_error()
        elif self.state == ErrorRecoveryState.Error:
            if self.last_success_read_write + self.config.fail_timeout_seconds < now:
                logger.debug(f"RW error, state transition: {ErrorRecoveryState.Error} -> {ErrorRecoveryState.Failure}")
                self.state = ErrorRecoveryState.Failure
                self.on_fail()

    # Callbacks

    def on_connect_error(self, exception: Exception):
        if self.connect_error_callback is not None:
            self.connect_error_callback(exception)

    def on_error(self):
        if self.error_callback is not None:
            self.error_callback()

    def on_fail(self):
        if self.fail_callback is not None:
            self.fail_callback()

    # Decorator impl

    def read(self, r: Register) -> Any:
        if RegisterDirection.Read not in r.direction:
            raise KeyError(f"Cannot read from register {r.name} which has direction {r.direction}")

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Failure]:
            raise HardwareLayerException(f"Cannot read in state {self.state}")

        if self.state == ErrorRecoveryState.Error:
            # in this state we are reconnecting. we do not want a possible success read to interfere
            # with reconnection. But we do want a possible transition to Failure so we note an error.
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

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Failure]:
            raise HardwareLayerException(f"Cannot read in state {self.state}")

        if self.state == ErrorRecoveryState.Error:
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

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Failure]:
            raise HardwareLayerException(f"Cannot write in state {self.state}")

        if self.state == ErrorRecoveryState.Error:
            self.error_read_write()
            self.pending_writes[r] = value
            return

        try:
            self.decorated.write(value, r)
            self.success_read_write()
            self._write_pending_values(except_names=[r.name])
        except HardwareLayerException:
            self.error_read_write()
            if self.state == ErrorRecoveryState.Failure:
                return
            self.pending_writes[r] = value


    def write_batch(self, values: Sequence[Any], registers: Sequence[Register]):
        for r in registers:
            if RegisterDirection.Write not in r.direction:
                raise KeyError(f"Cannot write to register {r.name} which has direction {r.direction}")

        if self.state in [ErrorRecoveryState.Disconnected, ErrorRecoveryState.Failure]:
            raise HardwareLayerException(f"Cannot write in state {self.state}")

        if self.state == ErrorRecoveryState.Error:
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
            if self.state == ErrorRecoveryState.Failure:
                return
            for value, r in zip(values, registers):
                self.pending_writes[r] = value

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

    def connect(self):
        try:
            self.decorated.connect()

            if self.state == ErrorRecoveryState.Disconnected:
                self.state = ErrorRecoveryState.OK

            self.connection_state = ConnectionStatusEnum.Connected
            self.last_success_connect = time.time()
        except HardwareLayerException:
            self.error_read_write()

    def disconnect(self):
        return self.decorated.disconnect()

    # could be a way to do it
    # def maintain_connection(self):
    #     if self.state == ErrorRecoveryState.Error:
    #         try:
    #             self.decoratee.connect()
