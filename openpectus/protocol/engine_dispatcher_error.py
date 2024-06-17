from __future__ import annotations

import asyncio
from datetime import datetime, UTC, timedelta
import logging

import openpectus.protocol.aggregator_messages as AM
from openpectus.protocol.engine_dispatcher import EngineDispatcher, EngineDispatcherBase, EngineMessageHandler
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolNetworkException
import openpectus.protocol.messages as M

logger = logging.getLogger(__name__)


class EngineDispatcherErrorRecoveryDecorator(EngineDispatcherBase):
    """
    Decorator that handles and masks connection errors that may occur in the Aggregator-Engine Protocol.
    """

    def __init__(self, decorated: EngineDispatcher, buffer_duration: timedelta = timedelta(seconds=5)) -> None:
        super().__init__()
        self._decorated = decorated
        self._buffer_duration = buffer_duration
        self._is_reconnecting = False
        self._is_reconnecting_disconnect = False
        self._message_buffer: dict[str, list[EM.EngineMessage]] = {}
        self._message_buffer_time: dict[str, datetime] = {}
        self._in_tick = False

    async def connect_async(self):
        try:
            await self._decorated.connect_async()
        except Exception:
            logger.warning("Connect failed")
            self._reconnect_begin()

    async def disconnect_async(self):
        try:
            await self._decorated.disconnect_async()
        except Exception:
            logger.error("Disconnect failed")

    def _reconnect_begin(self):
        self._is_reconnecting = True
        self._is_reconnecting_disconnect = True

    async def tick(self):
        if self._in_tick: # TODO use proper sync pattern
            logger.warning("Duplicate entry detected in dispatcher tick")
            return
        self._in_tick = True
        if self._is_reconnecting:
            if self._is_reconnecting_disconnect:
                try:
                    await asyncio.sleep(2)
                    await self._decorated.disconnect_async()
                    self._is_reconnecting_disconnect = False
                except Exception:
                    logger.warning("Reconnect - disconnect failed")  # , exc_info=True)
            else:
                try:
                    await asyncio.sleep(2)
                    await self._decorated.connect_async()
                    self._is_reconnecting = False
                    logger.info("Reconnect successful")
                except Exception:
                    logger.warning("Reconnect - connect failed")  # , exc_info=True)
        else:
            buffered_message_count = self._get_buffer_size()
            if buffered_message_count > 0:
                logger.info(f"Buffered messages remaining to be sent: {buffered_message_count}")
                message_batch = self._pop_buffer_batch()
                for message in message_batch:
                    try:
                        self._in_tick = False
                        response = await self._decorated.post_async(message)
                        if self._get_buffer_size() == 0:
                            logger.info("All caught up sending buffered messages")
                        return response
                    except Exception:
                        logger.error(f"Error sending buffered message {type(message).__name__}. Returning it to buffer",
                                     exc_info=True)
                        self._buffer_message(message)
        self._in_tick = False

    def _get_buffer_size(self) -> int:
        return sum([len(self._message_buffer[key]) for key in self._message_buffer.keys()])

    def _pop_buffer_batch(self) -> list[EM.EngineMessage]:
        # pick one message of each type to be sent
        buffers = [m for m in [self._message_buffer[key] for key in self._message_buffer.keys()]]
        messages = []
        for buffer in buffers:
            if len(buffer) > 0:
                messages.append(buffer.pop())
        return messages

    async def post_async(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        await self.tick()

        if self._is_reconnecting and isinstance(message, EM.EngineMessage):
            self._buffer_message(message)
            return M.ErrorMessage(message="Failed to send message")

        try:
            return await self._decorated.post_async(message)
        except ProtocolNetworkException:
            # maybe do something else for RegisterEngineMsg? like raise?
            logger.warning(f"Post failed for message {type(message).__name__}. Trying to recover")
            self._reconnect_begin()
            return M.ErrorMessage(message="Failed to send message")

    def set_rpc_handler(self, message_type: type[AM.AggregatorMessage], handler: EngineMessageHandler):
        """ Register handler for given message_type. """
        if message_type in self._decorated._handlers.keys():
            logger.error(f"Handler for message type {message_type} is already set.")
        self._decorated._handlers[message_type] = handler

    def _dispatch_message_async(self, message: M.MessageBase):
        return self._decorated._dispatch_message_async(message)

    def _buffer_message(self, message: EM.EngineMessage):
        now = datetime.now(UTC)
        msg_type = type(message).__name__
        if msg_type not in self._message_buffer_time.keys():
            self._message_buffer_time[msg_type] = now
            self._message_buffer[msg_type] = [message]
        else:
            if self._message_buffer_time[msg_type] + self._buffer_duration < now:
                logger.info(f"Buffering {msg_type} message")
                self._message_buffer[msg_type].append(message)
                self._message_buffer_time[msg_type] = now
