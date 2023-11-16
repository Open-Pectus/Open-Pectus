import unittest
from openpectus.aggregator.protocol import Aggregator
from openpectus.protocol.messages import RegisterEngineMsg, SuccessMessage, ErrorMessage
from fastapi_websocket_rpc.rpc_channel import RpcChannel, RpcMethodsBase


class AggregatorTest(unittest.IsolatedAsyncioTestCase):

    async def connectAggregator(self, aggregator: Aggregator, channel_id: str):
        await aggregator.on_connect(RpcChannel(RpcMethodsBase(), None, channel_id))

    async def disconnectAggregator(self, aggregator: Aggregator, channel_id: str):
        channel_info = aggregator.get_channel(channel_id)
        if channel_info is not None:
            await aggregator.on_disconnect(channel_info.channel)

    # TODO: can we test how many engines the aggregator would serve to frontend in the difference cases?

    async def test_register_engine_same_shannel(self):
        channel_id = 'test-channel'
        aggregator = Aggregator()
        register_engine_msg = RegisterEngineMsg(computer_name='computer-name', uod_name='uod-name')

        await self.connectAggregator(aggregator, channel_id)

        # registering while not registered before should succceed
        result = await aggregator.handle_RegisterEngineMsg(channel_id, register_engine_msg)
        self.assertIsInstance(result, SuccessMessage)

        # registering on same channel while already registered and still connected should fail
        result = await aggregator.handle_RegisterEngineMsg(channel_id, register_engine_msg)
        self.assertIsInstance(result, ErrorMessage)

        # registering on same channel while already registered, but after disconnect should succeed
        await self.disconnectAggregator(aggregator, channel_id)
        result = await aggregator.handle_RegisterEngineMsg(channel_id, register_engine_msg)
        self.assertIsInstance(result, SuccessMessage)

    async def test_register_engine_different_name(self):
        channel_id = 'test-channel'
        channel_id2 = 'test-channel2'
        aggregator = Aggregator()
        register_engine_msg = RegisterEngineMsg(computer_name='computer-name', uod_name='uod-name')
        register_engine_msg_different_computer = RegisterEngineMsg(computer_name='computer-name2', uod_name='uod-name')

        await self.connectAggregator(aggregator, channel_id)
        await self.connectAggregator(aggregator, channel_id2)

        # registering while not registered before should succceed
        result = await aggregator.handle_RegisterEngineMsg(channel_id, register_engine_msg)
        self.assertIsInstance(result, SuccessMessage)

        # registering on new channel while already registered with same name should fail
        result = await aggregator.handle_RegisterEngineMsg(channel_id2, register_engine_msg)
        self.assertIsInstance(result, ErrorMessage)

        # registering on new channel while already registered but with different name should succeed
        result = await aggregator.handle_RegisterEngineMsg(channel_id2, register_engine_msg_different_computer)
        self.assertIsInstance(result, SuccessMessage)


if __name__ == '__main__':
    unittest.main()
