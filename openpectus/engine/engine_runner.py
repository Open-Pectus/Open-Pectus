from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Awaitable, Callable, Literal

from openpectus.engine.engine_message_builder import EngineMessageBuilder
from openpectus.lang.exec.events import EventEmitter, EventListener, RunStateChange
from openpectus.protocol.engine_dispatcher import EngineDispatcher
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolNetworkException
import openpectus.protocol.messages as M

logger = logging.getLogger(__name__)

MAX_RECONNECT_WAIT_SECONDS = 10

RecoverState = Literal[
    "Started",
    "Connected",
    "Failed",
    "Disconnected", "Reconnecting", "CatchingUp", "Reconnected",
    "Stopped",
    "ShutdownComplete"
]

AsyncConnectionCallback = Callable[[], Awaitable[None]]
StateChangingCallback = Callable[[RecoverState, RecoverState], Awaitable[None]]

class AsyncTimer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.create_task(self._job(), name="engine.engine_runner.AsyncTimer")

    def __str__(self):
        return f'{self.__class__.__name__}(_task={self._task})'

    async def _job(self):
        try:
            while True:
                await asyncio.sleep(self._timeout)
                await self._callback()
        except asyncio.CancelledError:
            logger.debug("Cancelled AsyncTimer")

    def start(self):
        pass

    def stop(self):
        self._task.cancel()

class EngineRunner(EventListener):
    """
    Runner that implements error recovery and masks connection errors that may occur in the Aggregator-Engine Protocol.
    """

    # TODO: Remove raising ProtocolException where they are not caught which is most of them

    def __init__(self,
                 dispatcher: EngineDispatcher,
                 message_builder: EngineMessageBuilder,
                 emitter: EventEmitter,
                 loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self._dispatcher = dispatcher
        self._message_builder = message_builder
        self._state: RecoverState = "Started"
        self._message_buffer: list[EM.EngineMessage] = []
        self._lock = asyncio.Lock()
        self._state_task: asyncio.Task[None] | None = None
        self._transmit_buffer_task: asyncio.Task[None] | None = None
        self._timer = AsyncTimer(0.1, self._tick)
        self._first_steady_state = True
        self._loop = loop

        emitter.add_listener(self)

        self.connected_callback: AsyncConnectionCallback | None = None
        self.failed_callback: AsyncConnectionCallback | None = None
        self.catchingup_callback: AsyncConnectionCallback | None = None
        self.reconnecting_callback: AsyncConnectionCallback | None = None
        self.reconnected_callback: AsyncConnectionCallback | None = None
        self.state_changing_callback: StateChangingCallback | None = None
        self.first_steady_state_callback: AsyncConnectionCallback | None = None

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(dispatcher={self._dispatcher}, ' +
                f'message_builder={self._message_builder}, loop={self._loop}, state="{self.state}")')

    def on_start(self, run_id: str):
        super().on_start(run_id)
        if True or self.state == "Connected" or self.state == "Reconnected":
            msg = self._message_builder.create_run_started_msg(run_id, time.time())
            asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)
            msg = self._message_builder.create_wpn_run_started_msg()
            asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_stop(self):
        assert self.run_id is not None
        run_id = self.run_id
        super().on_stop()
        msg = self._message_builder.create_run_stopped_msg(run_id)
        asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)
        msg = self._message_builder.create_wpn_run_stopped_msg()
        asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_runstate_change(self, state_change):
        if state_change == RunStateChange.PAUSE:
            msg = self._message_builder.create_wpn_run_paused_msg()
            asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_block_start(self, block_info):
        msg = self._message_builder.create_wpn_block_started_msg(block_name=block_info.name)
        asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_notify_command(self, argument):
        msg = self._message_builder.create_wpn_notify_command_msg(text=argument)
        asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_scope_activate(self, scope_info):
        if scope_info.scope_type == "Watch":
            msg = self._message_builder.create_wpn_watch_activated_msg(watch_argument=scope_info.argument)
            asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_method_error(self, exception):
        msg = self._message_builder.create_wpn_method_error_msg()
        asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    def on_connection_status_change(self, status):
        msg = self._message_builder.create_wpn_network_error_msg()
        asyncio.run_coroutine_threadsafe(self._post_async(msg), self._loop)

    @property
    def state(self) -> RecoverState:
        return self._state

    async def run(self):
        self._timer.start()

        while self.state != "ShutdownComplete":
            await asyncio.sleep(0.2)
        self._timer.stop()
        await self._timer._task

    async def _connect_async(self):
        if self.state == "Stopped":
            return
        elif self.state == "Started" or self.state == "Disconnected":
            pass
        else:
            err_msg = f"Invalid operation '_connect_async' for state: {self.state}"
            logger.error(err_msg)

        try:
            await self._dispatcher.connect_async()

            # Note: Consider adding a ping to verify connection.
            # resp = await self._dispatcher.post_async(EM.PingMsg())
            # if resp is None or not isinstance(resp, M.SuccessMessage):
            #     raise Exception("Negative Ping result")

            if self.state == "Started":
                await self._set_state("Connected")
            elif self.state == "Disconnected":
                await self._set_state("Reconnecting")
            logger.info("Connect successful")

        except ProtocolNetworkException:
            await self._set_state("Failed")
            logger.warning("Connect failed")
        except Exception:
            await self._set_state("Failed")
            logger.error("Connect failed with unhandled exception", exc_info=True)

    async def _disconnect_async(self, set_state_disconnected=True):
        if self.state == "Stopped":
            pass
        elif self.state == "Failed":
            pass
        else:
            err_msg = f"Invalid operation '_disconnect_async' for state: {self.state}"
            logger.error(err_msg)

        try:
            await self._dispatcher.disconnect_async()
        except Exception:
            logger.warning("Disconnect failed")
        finally:
            if set_state_disconnected:
                await self._set_state("Disconnected")

    async def shutdown(self):
        await self._set_state("Stopped")
        await self._disconnect_async(set_state_disconnected=False)
        await self._set_state("ShutdownComplete")

    async def _post_async(self, message: EM.EngineMessage) -> M.MessageBase:
        states_to_post: list[RecoverState] = ["Connected", "Reconnected", "CatchingUp"]
        states_to_buffer: list[RecoverState] = ["Failed", "Disconnected", "Reconnecting"]

        if self.state == "Stopped":
            return M.ErrorMessage(message="System is down")

        elif self.state in states_to_post:
            try:
                return await self._dispatcher.send_async(message)
            except ProtocolNetworkException:
                await self._set_state("Failed")
                logger.warning(f"Failed to send message {message.ident}, adding to buffer")
                self._buffer_message(message)
                return M.ErrorMessage(message="Failed to send message, was added to buffer")

        elif self.state in states_to_buffer:
            self._buffer_message(message)
            return M.ErrorMessage(message="Failed to send message, was added to buffer")

        else:
            err_msg = f"Invalid operation 'post_async' for state: {self.state}"
            logger.error(err_msg)
            return M.ErrorMessage(message="Failed to send message, invalid state")

    async def _tick(self):
        async with self._lock:
            if self._state == "Stopped":
                return

            elif self._state == "Connected" or self._state == "Reconnected":
                # steady state
                pass

            elif self._state == "Started":
                await self._connect_async()

            elif self._state == "Failed":
                await self._disconnect_async()

            elif self._state == "Disconnected":
                wait_secs = random.uniform(0.5, MAX_RECONNECT_WAIT_SECONDS)
                logger.debug(f"Waiting {wait_secs:0.1f} seconds before reconnecting")
                await asyncio.sleep(wait_secs)
                await self._connect_async()

            elif self._state == "Reconnecting":
                await self._set_state("CatchingUp")

            elif self._state == "CatchingUp":
                if (self._transmit_buffer_task is None or (self._transmit_buffer_task is not None and self._transmit_buffer_task.done())):
                    self._transmit_buffer_task = asyncio.create_task(self._send_buffered_batch())


    async def _set_state(self, state: RecoverState):
        prev_state = self.state
        logger.info(f"Changing state: {prev_state} -> {state}")
        if self.state_changing_callback is not None:
            await self.state_changing_callback(self.state, state)

        self._state = state

        if self._state_task is not None:
            # cancel the long running task, except if its the fail/buffer task and we're still
            # working to reconnect
            if (state == "Failed" or state == "Disconnected" or state == "Reconnecting"
                    or state == "CatchingUp") and self._state_task.get_name() == "engine.engine_runner.buffer_messages":
                pass
            else:
                logger.debug("Cancelling state task " + self._state_task.get_name())
                self._state_task.cancel()
                try:
                    await self._state_task  # Await cancellation
                    self._state_task = None
                    logger.debug("State task finished")
                except asyncio.CancelledError:
                    logger.debug("State task cancelled")
                    self._state_task = None


        if self._transmit_buffer_task is not None:
            if state == "Reconnected":
                logger.debug("Cancelling buffer transmission task")
                self._transmit_buffer_task.cancel()
                try:
                    await self._transmit_buffer_task  # Await cancellation
                    self._transmit_buffer_task = None
                    logger.debug("Buffer transmission task finished")
                except asyncio.CancelledError:
                    logger.debug("Buffer transmission task cancelled")
                    self._transmit_buffer_task = None


        if state in ["Connected", "CatchingUp"]:
            await self._on_connection_established()

        if state == "Connected":
            await self._on_connected()
        elif state == "Failed":
            self._dispatcher._engine_id = None
            await self._on_failed()
        elif state == "CatchingUp":
            await self._on_catchingup()
        elif state == "Reconnecting":
            await self._on_reconnecting()
        elif state == "Reconnected":
            await self._on_reconnected()

    async def _send_buffered_batch(self):
        if self._state == "Stopped":
            return

        if self._state != "CatchingUp":
            err_msg = f"Invalid operation '_send_buffered_batch' for state: {self.state}"
            logger.warning(err_msg)

        await self._post_async(self._message_builder.create_method_msg())
        buffered_message_count = self._get_buffer_size()
        if buffered_message_count > 0:
            message_buffer = self._message_buffer.copy()
            self._message_buffer.clear()
            n_buffer = len(message_buffer)
            logger.info(f"Sending {n_buffer} buffered messages")
            # Wrap _post_async to print out some progress.
            i = 0
            async def wrap(message):
                nonlocal i
                await self._post_async(message)
                i += 1
                if i % (n_buffer//10) == 0:
                    logger.info(f"Submitted {i} of {n_buffer} buffered messages")
            # Only wrap if there is a substantial amount of messages
            fn_calls = []
            if n_buffer < 100:
                fn_calls = [self._post_async(message) for message in message_buffer]
            else:
                fn_calls = [wrap(message) for message in message_buffer]
            await asyncio.gather(*fn_calls)
            logger.debug("Done sending batch")
        else:
            logger.info("All caught up sending buffered messages")
            await self._set_state("Reconnected")

    def _buffer_message(self, message: EM.EngineMessage):
        """ Append message to the buffer """
        self._dispatcher.assign_sequence_number(message)
        logger.debug(f"Buffering message: {message.ident}")
        self._message_buffer.append(message)

    def _get_buffer_size(self) -> int:
        return len(self._message_buffer)

    async def _on_connection_established(self):
        await self._post_async(self._message_builder.create_uod_info())

    async def _on_connected(self):
        logger.debug("on_connected")
        if self.connected_callback is not None:
            await self.connected_callback()
        await self.on_steady_state()

    async def buffer_messages(self):
        logger.info("Started buffer_messages loop")
        while self._state_task and self._state_task.cancelling() == 0:
            if self.state == "Stopped":
                return
            for msg in [
                self._message_builder.create_tag_updates_msg(),
                self._message_builder.create_method_state_msg(),
                self._message_builder.create_error_log_msg(),
            ]:
                if msg is not None:
                    self._buffer_message(msg)
            await asyncio.sleep(5)
        logger.info("Stopped buffer_messages loop")

    async def _on_failed(self):
        logger.debug("on_failed")

        # need to run long running job in spawn task
        if self._state_task is None:
            self._state_task = asyncio.create_task(self.buffer_messages(), name="engine.engine_runner.buffer_messages")
        elif self._state_task.get_name() == "engine.engine_runner.buffer_messages":
            pass
        else:
            logger.error(f"Attempting to start buffer_messages task while other task is allocated: {self._state_task}")

    async def _on_reconnecting(self):
        logger.debug("on_reconnecting")
        if self.reconnecting_callback is not None:
            await self.reconnecting_callback()

    async def _on_catchingup(self):
        logger.debug("on_catchingup")
        if self.catchingup_callback is not None:
            await self.catchingup_callback()

    async def _on_reconnected(self):
        logger.debug("on_reconnected")
        if self.reconnected_callback is not None:
            await self.reconnected_callback()
        await self.on_steady_state()

    async def steady_state_send_messages(self):
        logger.info("Started steady-state sending loop")
        await self._post_async(self._message_builder.create_tag_updates_snapshot_msg())
        while self._state_task and self._state_task.cancelling() == 0:
            messages = []
            try:
                messages = [
                    self._message_builder.create_control_state_msg(),
                    self._message_builder.create_method_state_msg(),
                    self._message_builder.create_error_log_msg(),
                    self._message_builder.create_tag_updates_msg(),
                ]
                if self.run_id is not None:
                    messages.append(self._message_builder.create_runlog_msg(self.run_id))
            except asyncio.CancelledError:
                return # or raise?
            except Exception:
                logger.error("Exception occurred building messages", exc_info=True)

            # Post of messages can be shielded from cancellation. It is OK that they finish so long
            # as the loop stops. This task is cancelled when connection fails and this is handled
            # by _post_async anyways.
            await asyncio.shield(asyncio.gather(*[self._post_async(msg) for msg in messages if msg is not None]))
            await asyncio.sleep(0.3)
        logger.info("Stopped steady-state sending loop")

    async def on_steady_state(self):
        """ Steady-State message sending loop """

        # raise first steady state event that should start engine
        if self._first_steady_state:
            self._first_steady_state = False
            if self.first_steady_state_callback is not None:
                await self.first_steady_state_callback()

        # Send message in concurrent task
        if self._state_task is None:
            self._state_task = asyncio.create_task(self.steady_state_send_messages(), name="engine.engine_runner.steady_state_send_messages")
        else:
            logger.error(f"Attempting to start send_messages task while other task is allocated: {self._state_task}")
