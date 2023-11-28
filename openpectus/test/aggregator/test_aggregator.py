import asyncio
import unittest
from unittest.mock import Mock, AsyncMock

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
from fastapi_websocket_rpc.schemas import RpcResponse
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher


class AggregatorTest(unittest.IsolatedAsyncioTestCase):

    async def create_channel_mock(self, engine_id: str | None):
        response = RpcResponse[str | None](result=engine_id, result_type=None)
        return Mock(close=AsyncMock(), other=Mock(get_engine_id=AsyncMock(return_value=response)))

    async def connectRpc(self, dispatcher: AggregatorDispatcher, engine_id: str | None):
        channel = await self.create_channel_mock(engine_id)
        await dispatcher.on_delayed_client_connect(channel)
        return channel

    async def disconnectRpc(self, dispatcher: AggregatorDispatcher, engine_id: str):
        channel = dispatcher._engine_id_channel_map[engine_id]
        await dispatcher.on_client_disconnect(channel)

    async def test_register_engine(self):
        dispatcher = AggregatorDispatcher()
        aggregator = Aggregator(dispatcher)
        messageHandlers = AggregatorMessageHandlers(aggregator)
        register_engine_msg = EM.RegisterEngineMsg(computer_name='computer-name', uod_name='uod-name')
        engine_id = aggregator.create_engine_id(register_engine_msg)

        # connecting rpc with no response for engine id should close connection
        channel = await self.connectRpc(dispatcher, None)
        channel.close.assert_called()

        # registering while not registered before should succceed
        resultMessage = await dispatcher._dispatch_post(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, True)

        # connecting rpc now should not close connection
        channel = await self.connectRpc(dispatcher, engine_id)
        channel.close.assert_not_called()

        # registering while already registered and still connected should fail
        resultMessage = await dispatcher._dispatch_post(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, False)

        # registering while already registered, but after disconnect should succeed
        await self.disconnectRpc(dispatcher, engine_id)
        resultMessage = await dispatcher._dispatch_post(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, True)

    async def test_register_engine_different_name(self):
        dispatcher = AggregatorDispatcher()
        aggregator = Aggregator(dispatcher)
        messageHandlers = AggregatorMessageHandlers(aggregator)
        register_engine_msg = EM.RegisterEngineMsg(computer_name='computer-name', uod_name='uod-name')
        register_engine_msg_different_computer = EM.RegisterEngineMsg(computer_name='computer-name2', uod_name='uod-name')
        engine_id1 = aggregator.create_engine_id(register_engine_msg)
        engine_id2 = aggregator.create_engine_id(register_engine_msg_different_computer)

        # registering engine 1 while not registered before should succceed
        resultMessage = await messageHandlers.handle_RegisterEngineMsg(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, True)

        # connecting rpc now for registered engine should not close connection
        channel = await self.connectRpc(dispatcher, engine_id1)
        channel.close.assert_not_called()

        # registering while already registered with same name should fail
        resultMessage = await messageHandlers.handle_RegisterEngineMsg(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, False)

        # registering while already registered but with different name should succeed
        resultMessage = await messageHandlers.handle_RegisterEngineMsg(register_engine_msg_different_computer)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, True)


if __name__ == '__main__':
    unittest.main()
