from __future__ import annotations

import asyncio
import logging
import random
import time
from typing import Awaitable, Callable, Literal

from openpectus.engine.engine_message_builder import EngineMessageBuilder
from openpectus.lang.exec.tag_lifetime import TagContext, TagLifetime
from openpectus.protocol.engine_dispatcher import EngineDispatcher
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolException, ProtocolNetworkException
import openpectus.protocol.messages as M

logger = logging.getLogger(__name__)

MAX_RECONNECT_WAIT_SECONDS = 10
BUFFER_BATCH_SIZE = 10

RecoverState = Literal[
    "Started",
    "Connected",
    "Failed",
    "Disconnected", "Reconnecting", "CatchingUp", "Reconnected",
    "Stopped"
]

AsyncConnectionCallback = Callable[[], Awaitable[None]]
StateChangingCallback = Callable[[RecoverState, RecoverState], Awaitable[None]]

class AsyncTimer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = asyncio.ensure_future(self._job())
        self._running = False

    async def _job(self):
        while self._running:
            await asyncio.sleep(self._timeout)
            await self._callback()

    def start(self):
        self._running = True

    def stop(self):
        self._running = False
        self._task.cancel()


class Lifetime(TagLifetime):
    """ Watches engine state changes and makes them available to EngineRunner. """
    def __init__(self, on_start, on_stop) -> None:
        super().__init__()
        self.on_start_cb = on_start
        self.on_stop_cb = on_stop
        self.run_id: str | None = None

    @property
    def has_active_run(self) -> bool:
        return self.run_id is not None

    def on_start(self, context: TagContext, run_id: str):
        # Note: callback is invoked after setting run_id
        self.run_id = run_id
        self.on_start_cb()

    def on_stop(self):
        # Note: callback is invoked before clearing run_id
        self.on_stop_cb()
        self.run_id = None


class EngineRunner():
    """
    Handles engine message sending and and masks connection errors that may occur in the Aggregator-Engine Protocol.
    """

    def __init__(self, dispatcher: EngineDispatcher, message_builder: EngineMessageBuilder,
                 event_context: TagContext) -> None:
        super().__init__()
        self._dispatcher = dispatcher
        self._message_builder = message_builder
        self._state: RecoverState = "Started"
        self._message_buffer: list[EM.EngineMessage] = []
        self._priority_msg: EM.EngineMessage | None = None
        self._lock = asyncio.Lock()
        self._reconnect_msg : EM.ReconnectedMsg | None = None
        self._state_task: asyncio.Task[None] | None = None
        self._timer = AsyncTimer(0.1, self._tick)
        self._first_steady_state = True

        self.connected_callback: AsyncConnectionCallback | None = None
        self.failed_callback: AsyncConnectionCallback | None = None
        self.catchingup_callback: AsyncConnectionCallback | None = None
        self.reconnecting_callback: AsyncConnectionCallback | None = None
        self.reconnected_callback: AsyncConnectionCallback | None = None
        self.state_changing_callback: StateChangingCallback | None = None
        self.first_steady_state_callback: AsyncConnectionCallback | None = None

        # listen to engine events because we need to adapt the messages to send
        # to current engine state
        self.lifetime = Lifetime(self._on_run_start, self._on_run_stop)
        event_context.add_listener(self.lifetime)

    def _set_priority_msg(self, msg: EM.EngineMessage):
        if self._priority_msg is not None:
            logger.warning(f"Setting prio msg {msg.ident} when another {self._priority_msg.ident} was already set")
        self._priority_msg = msg

    def _clear_priority_msg(self):
        self._priority_msg = None

    def _on_run_start(self):
        if self.state == "Connected" or self.state == "Reconnected":
            assert self.lifetime.run_id is not None
            msg = self._message_builder.create_run_started_msg(self.lifetime.run_id, time.time())
            # We cant send immidiately because we're invoked fron a sync event. Instead we schedule sending
            # as a priority message
            self._set_priority_msg(msg)
        else:
            raise Exception("Cannot send RunStartedMsg when not connected")

    def _on_run_stop(self):
        if self.lifetime.run_id is None:
            logger.error("Cannot send RunStoppedMsg when no run_id has been set")
            return
        if self.state == "Connected" or self.state == "Reconnected":
            msg = self._message_builder.create_run_stopped_msg(self.lifetime.run_id)
            self._set_priority_msg(msg)
        else:
            raise Exception("Cannot send RunStartedMsg when not connected")

    @property
    def state(self) -> RecoverState:
        return self._state

    async def run(self):
        self._timer.start()

        while self.state != "Stopped":
            await asyncio.sleep(0.2)

    async def _connect_async(self):
        if self.state == "Stopped":
            return
        elif self.state == "Started" or self.state == "Disconnected":
            pass
        else:
            err_msg = f"Invalid operation '_connect_async' for state: {self.state}"
            logger.error(err_msg)
            raise ProtocolException(err_msg)

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
            return
        elif self.state == "Failed":
            pass
        else:
            err_msg = f"Invalid operation '_disconnect_async' for state: {self.state}"
            logger.error(err_msg)
            raise ProtocolException(err_msg)

        try:
            await self._dispatcher.disconnect_async()
        except Exception:
            logger.warning("Disconnect failed")
        finally:
            if set_state_disconnected:
                await self._set_state("Disconnected")

    async def shutdown(self):
        async with self._lock:
            await self._set_state("Stopped")
            self._timer.stop()
            await self._disconnect_async(set_state_disconnected=False)

    async def _post_async(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        states_to_post: list[RecoverState] = ["Connected", "Reconnected", "CatchingUp"]
        states_to_buffer: list[RecoverState] = ["Failed", "Disconnected", "Reconnecting"]

        if self.state == "Stopped":
            return M.ErrorMessage(message="System is down")

        elif self.state in states_to_post:
            try:
                if self._priority_msg is not None:
                    await self._dispatcher.post_async(self._priority_msg)
                    logger.debug(f"Sent priority message: {self._priority_msg.ident}")
                    self._clear_priority_msg()
            except Exception:
                logger.error(f"Failed to send prio msg: {self._priority_msg}", exc_info=True)
                # TODO what to do here?
            try:
                return await self._dispatcher.post_async(message)
            except ProtocolNetworkException:
                await self._set_state("Failed")
                logger.warning(f"Failed to send message {message.ident}, adding to buffer")
                if isinstance(message, EM.RegisterEngineMsg):
                    err_msg = f"Invalid message RegisterEngineMsg in state: {self.state}"
                    raise ProtocolException(err_msg)
                else:
                    self._buffer_message(message)
                    return M.ErrorMessage(message="Failed to send message, was added to buffer")

        elif self.state in states_to_buffer:
            if isinstance(message, EM.RegisterEngineMsg):
                raise
            else:
                if self.lifetime.has_active_run:  # Not sure is this check belongs here or to just not create this message
                    self._buffer_message(message)
                    return M.ErrorMessage(message="Failed to send message, was added to buffer")
                else:
                    logger.debug("No active run, skip message")
        else:
            err_msg = f"Invalid operation 'post_async' for state: {self.state}"
            logger.error(err_msg)
            raise ProtocolException(err_msg)

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
                await self._send_reconnect_msg()

            elif self._state == "CatchingUp":
                await self._send_buffered_batch()

    async def _send_reconnect_msg(self):
        if self._state == "Stopped":
            return
        elif self.state == "Reconnecting":
            if self._reconnect_msg is None:
                logger.error("No reconnect message")
                raise ProtocolException()
            else:
                try:
                    logger.debug("Sending reconnect msg")
                    await self._dispatcher.post_async(self._reconnect_msg)
                    logger.debug("Reconnect msg sent")
                    self._reconnect_msg = None
                except ProtocolNetworkException:
                    logger.warning("Failed to send reconnect message")
                    await asyncio.sleep(1)
                    await self._set_state("Failed")
                    return
                except Exception:
                    logger.error("Failed to send reconnect message. Unhandled exception", exc_info=True)
                    await asyncio.sleep(1)
                    await self._set_state("Failed")
                    return

                await self._set_state("CatchingUp")
        else:
            err_msg = f"Invalid operation '_send_reconnect_msg' for state: {self.state}"
            logger.error(err_msg)
            raise ProtocolException(err_msg)

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
                    or state == "CatchingUp") and self._state_task.get_name() == "buffer_messages":
                pass
            else:
                logger.debug("Cancelling state task " + self._state_task.get_name())
                self._state_task.cancel()
                self._state_task = None

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
            logger.error(err_msg)
            raise ProtocolException(err_msg)

        buffered_message_count = self._get_buffer_size()
        if buffered_message_count > 0:
            message_batch = self._pop_buffer_batch()
            if __debug__:
                logger.debug(f"Buffered messages remaining to be sent: {buffered_message_count}")
                logger.debug(f"Buffer: {EM.print_sequence_range(self._message_buffer)}")
                logger.debug(f"Batch : {EM.print_sequence_range(message_batch)}")

            for message in message_batch:
                await self._post_async(message)
                await asyncio.sleep(0.3)
            logger.debug("Done sending batch")
        else:
            logger.info("All caught up sending buffered messages")
            await self._set_state("Reconnected")

    def _buffer_message(self, message: EM.EngineMessage):
        """ Append message to the buffer """
        if isinstance(message, EM.ReconnectedMsg):
            err_msg = f"Invalid operation. ReconnectedMsg should not be buffered. State: {self.state}"
            logger.error(err_msg)
            raise ProtocolException(err_msg)
        else:
            self._dispatcher.assign_sequence_number(message)
            logger.debug(f"Buffering message: {message.ident}")
            self._message_buffer.append(message)

    def _get_buffer_size(self) -> int:
        return len(self._message_buffer)

    def _pop_buffer_batch(self) -> list[EM.EngineMessage]:
        messages = []
        for _ in range(BUFFER_BATCH_SIZE):
            if len(self._message_buffer) > 0:
                messages.append(self._message_buffer.pop(0))
        return messages

    async def _on_connected(self):
        logger.debug("on_connected")
        if self.connected_callback is not None:
            await self.connected_callback()
        await self.on_steady_state()

    async def _on_failed(self):
        logger.debug("on_failed")

        if self._reconnect_msg is None:
            self._reconnect_msg = self._message_builder.build_reconnected_message()

        if not self.lifetime.has_active_run:
            # TODO verify this. Do we really need reconnect_msg in this case?
            # need to specify the purpose of reconnect_msg in aggregator terms
            logger.debug("Failed while no run is active. Skip starting the buffering task")
            return

        async def buffer_messages():
            logger.info("Started buffer_messages loop")
            while True:
                for msg in [
                    self._message_builder.create_tag_updates_msg(),
                    self._message_builder.create_method_state_msg(),
                    self._message_builder.create_error_log_msg(),
                ]:
                    if msg is not None:
                        self._buffer_message(msg)
                await asyncio.sleep(5)

        # need to run long running job in spawn task
        if self._state_task is None:
            self._state_task = asyncio.create_task(buffer_messages(), name="buffer_messages")

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

    async def on_steady_state(self):
        """ Steady-State message sending loop """

        # raise first steady state event that should start engine
        if self._first_steady_state:
            self._first_steady_state = False
            if self.first_steady_state_callback is not None:
                await self.first_steady_state_callback()

        async def send_messages():
            logger.info("Started steady-state sending loop")
            await self._post_async(self._message_builder.create_uod_info())
            await self._post_async(self._message_builder.create_tag_updates_snapshot_msg())
            await asyncio.sleep(1)
            while True:
                messages: list[EM.EngineMessage | None] = []
                try:
                    if self.lifetime.run_id is None:
                        # when no run is active, we don't need to send much
                        # TODO: consider the first invocation after state change though - will control_state be sent then?
                        messages.append(self._message_builder.create_tag_updates_msg())
                    else:
                        messages.append(self._message_builder.create_control_state_msg())
                        messages.append(self._message_builder.create_method_state_msg())
                        messages.append(self._message_builder.create_error_log_msg())                        
                        messages.append(self._message_builder.create_runlog_msg(self.lifetime.run_id))
                        messages.append(self._message_builder.create_tag_updates_msg())
                except Exception:
                    logger.error("Exception occurred building messages", exc_info=True)
                    await asyncio.sleep(1)

                try:
                    for msg in messages:
                        if msg is not None:
                            await self._post_async(msg)
                            logger.debug(f"Sent message: {msg.ident}")
                except Exception:
                    logger.error("Exception occurred sending messages", exc_info=True)

                await asyncio.sleep(1)

        # need to run long running job in spawn task
        self._state_task = asyncio.create_task(send_messages(), name="send_messages")

    def __str__(self) -> str:
        return f"EngineRunner(state: {self.state}, run_id: {self.lifetime.run_id})"
