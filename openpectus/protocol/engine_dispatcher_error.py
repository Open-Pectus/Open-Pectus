from __future__ import annotations

import asyncio
from datetime import timedelta
import logging
from typing import Awaitable, Callable

import openpectus.protocol.aggregator_messages as AM
from openpectus.protocol.engine_dispatcher import EngineDispatcher, EngineDispatcherBase, EngineMessageHandler
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolNetworkException
import openpectus.protocol.messages as M

logger = logging.getLogger(__name__)

ConnectionCallback = Callable[[], None]
AsyncConnectionCallback = Callable[[], Awaitable[None]]

class EngineDispatcherErrorRecoveryDecorator(EngineDispatcherBase):
    """
    Decorator that handles and masks connection errors that may occur in the Aggregator-Engine Protocol.
    """

    #def __init__(self, decorated: EngineDispatcher, buffer_duration: timedelta = timedelta(seconds=5)) -> None:
    def __init__(self, decorated: EngineDispatcher, buffer_duration: timedelta = timedelta(milliseconds=1)) -> None:
        super().__init__()
        self._decorated = decorated
        self._buffer_duration = buffer_duration
        self._is_reconnecting = False
        self._is_reconnecting_disconnect = False
        self._message_buffer: list[EM.EngineMessage] = []
        self._lock = asyncio.Lock()
        self.connected_callback: ConnectionCallback | None = None
        self.reconnected_callback: AsyncConnectionCallback | None = None
        self.disconnected_callback: ConnectionCallback | None = None
        self.was_connected = False
        self.buf_recon = False

    async def connect_async(self):
        try:
            await self._decorated.connect_async()
            logger.info("Connect successful")
            if not self.was_connected:
                self.was_connected = True
                self._on_connected()
        except Exception:
            logger.warning("Connect failed")
            self._reconnect_begin()

    async def disconnect_async(self):
        try:
            await self._decorated.disconnect_async()
        except Exception:
            logger.error("Disconnect failed")
        finally:
            self._on_disconnected()

    async def post_async(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        await self._tick()

        if self._is_reconnecting and isinstance(message, EM.EngineMessage):
            self._buffer_message(message)
            return M.ErrorMessage(message="Failed to send message, was added to buffer")

        # Aggregator requires original message order is maintained to process messages correctly.
        # If buffer is non-empty, add to buffer instead of sending.
        # Register message is special, though, as usual
        if self._get_buffer_size() > 0 and not isinstance(message, EM.RegisterEngineMsg):
            self._buffer_message(message)
            logger.debug(f"Message {message.ident} too new, was added to buffer")
            return M.ErrorMessage(message="Message too new, was added to buffer")
        else:
            try:
                return await self._decorated.post_async(message)
            except ProtocolNetworkException:
                if isinstance(message, EM.RegisterEngineMsg):
                    logger.debug("Register message was not buffered")
                    raise ProtocolNetworkException("RegisterEngineMsg should not be buffered when disconnected")
                else:
                    self._buffer_message(message)
                    logger.warning(f"Post failed for message {type(message).__name__}. Trying to recover")
                    self._reconnect_begin()
                    return M.ErrorMessage(message="Failed to send message")

    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        """ Register handler for given message_type. """
        if message_type in self._decorated._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._decorated._handlers[message_type] = handler

    def dispatch_message_async(self, message: M.MessageBase):
        return self._decorated.dispatch_message_async(message)

    def assign_sequence_number(self, message: EM.EngineMessage | EM.RegisterEngineMsg):
        self._decorated.assign_sequence_number(message)

    def _reconnect_begin(self):
        self._is_reconnecting = True
        self._is_reconnecting_disconnect = True
        self._decorated._engine_id = None

    async def _tick(self):
        """ advances the reconnect state or sends buffered messages """
        async with self._lock:
            if self._is_reconnecting:
                if self._is_reconnecting_disconnect:
                    try:
                        await asyncio.sleep(2)
                        self._is_reconnecting_disconnect = False  # we only attempt disconnect once
                        await self._decorated.disconnect_async()
                        self._on_disconnected()
                    except Exception:
                        logger.warning("Reconnect - disconnect failed")
                else:
                    try:
                        await asyncio.sleep(2)
                        await self._decorated.connect_async()
                        logger.info("Reconnect successful")
                        # Note: important to clear this flag here rather than
                        # in connect_async() to avoid registration failure
                        self._is_reconnecting = False
                        asyncio.create_task(self._on_reconnected())  # avoid deadlock
                    except Exception:
                        logger.warning("Reconnect - connect failed")
            else:
                await self._send_buffered_messages()

    async def _send_buffered_messages(self):
        if not self.buf_recon:
            return
        buffered_message_count = self._get_buffer_size()
        if buffered_message_count > 0:
            logger.debug(f"Buffered messages remaining to be sent: {buffered_message_count}")
            message_batch = self._pop_buffer_batch()
            logger.debug(f"Buffer sq: {','.join([str(m.sequence_number) for m in self._message_buffer])}")
            logger.debug(f"Batch sq : {','.join([str(m.sequence_number) for m in message_batch])}")

            for message in message_batch:
                logger.info(f"Sending buffered message {message.ident}")
                # last_message_tick_time = 0
                # for i, m in enumerate(message_batch):                            
                #     if isinstance(m, EM.TagsUpdatedMsg):
                #         if len(m.tags) > 0:
                #             logger.info(f"Msg {m.ident}")
                #             message_tick_time = m.tags[0].tick_time
                #             if message_tick_time < last_message_tick_time:
                #                 logger.error("Hmm - message has time earlier than previous message")
                #             last_message_tick_time = message_tick_time
                try:
                    _ = await self._decorated.post_async(message)
                except ProtocolNetworkException:
                    logger.error(f"Error sending buffered message {message.ident}. Returning it to buffer")
                    logger.debug("err", exc_info=True)
                    self._buffer_message(message)
            if self._get_buffer_size() == 0:
                logger.info("All caught up sending buffered messages")

    def _buffer_message(self, message: EM.EngineMessage):
        """ Append message to the buffer """
        msg_type = type(message).__name__
        self.assign_sequence_number(message)
        if isinstance(message, EM.ReconnectedMsg):
            logger.debug("ReconnectedMsg replaces buffer")
            self._message_buffer = [message]
            self.buf_recon = True
        else:
            logger.info(f"Buffering {msg_type} message")
            self._message_buffer.append(message)

    def _get_buffer_size(self) -> int:
        return len(self._message_buffer)

    def _pop_buffer_batch(self) -> list[EM.EngineMessage]:
        # pick messages of each type to be sent. buffers use original message order for each type of message        
        messages = []
        for _ in range(5):
            if len(self._message_buffer) > 0:
                messages.append(self._message_buffer.pop(0))
        return messages

    def _on_connected(self):
        logger.debug("on_connected")
        if self.connected_callback is not None:
            self.connected_callback()

    async def _on_reconnected(self):
        logger.debug("on_reconnected")
        if self.reconnected_callback is not None:
            await self.reconnected_callback()

    def _on_disconnected(self):
        logger.debug("on_disconnected")
        self.buf_recon = False
        if self.disconnected_callback is not None:
            self.disconnected_callback()
