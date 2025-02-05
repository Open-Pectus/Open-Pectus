from __future__ import annotations
import asyncio
from dataclasses import dataclass
import logging
import unittest

from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import SystemStateEnum
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_message_builder import EngineMessageBuilder
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
import openpectus.protocol.aggregator_messages as AM
from openpectus.protocol.engine_dispatcher import EngineDispatcher
from openpectus.engine.engine_runner import EngineRunner
import openpectus.protocol.engine_messages as EM
from openpectus.protocol.exceptions import ProtocolException, ProtocolNetworkException
import openpectus.protocol.messages as M
from fastapi_websocket_rpc.logger import get_logger
from openpectus.aggregator.aggregator import Aggregator

from openpectus.test.engine.test_engine import create_test_uod
import openpectus.aggregator.data.models as DMdl


logging.basicConfig()
logger = get_logger("Test")
logger.setLevel(logging.DEBUG)

logging.getLogger('asyncio').setLevel(logging.ERROR)
logging.getLogger('openpectus.engine.engine_message_handlers').setLevel(logging.DEBUG)
logging.getLogger('openpectus.protocol.engine_dispatcher').setLevel(logging.DEBUG)
logging.getLogger('openpectus.engine.engine_runner').setLevel(logging.DEBUG)
logging.getLogger('openpectus.aggregator.aggregator').setLevel(logging.DEBUG)
logging.getLogger('openpectus.protocol.aggregator_dispatcher').setLevel(logging.DEBUG)


class ProtocolIntegrationTestCase(unittest.IsolatedAsyncioTestCase):
    ctx: ProtocolIntegrationTestCase.Context | None = None

    @dataclass
    class Context:
        """ Test helper class """
        engine: Engine
        engineDispatcher: EngineTestDispatcher
        engineRunner: EngineRunner
        engineMessageHandlers: EngineMessageHandlers

        aggregatorDispatcher: AggregatorTestDispatcher
        frontendPublisher: FrontendPublisher
        aggregator: Aggregator

    async def asyncSetUp(self) -> None:
        assert self.ctx is None
        await super().asyncSetUp()

        # setup in-memory database
        database.configure_db("sqlite:///:memory:")
        DMdl.DBModel.metadata.create_all(database._engine)  # type: ignore

        # the test class IsolatedAsyncioTestCase provides the event loop
        loop = asyncio.get_running_loop()

        uod = create_test_uod()
        engine = Engine(uod)
        engineDispatcher = EngineTestDispatcher()
        engineRunner = EngineRunner(engineDispatcher, EngineMessageBuilder(engine), engine.emitter, loop)
        engineMessageHandlers = EngineMessageHandlers(engine, engineDispatcher)

        aggregatorDispatcher = AggregatorTestDispatcher()
        frontendPublisher = FrontendPublisher()
        aggregator = Aggregator(aggregatorDispatcher, frontendPublisher)
        _ = AggregatorMessageHandlers(aggregator)

        # connect the two test dispatchers for direct communication
        aggregatorDispatcher.engineDispatcher = engineDispatcher
        engineDispatcher.aggregatorDispatcher = aggregatorDispatcher

        self.ctx = ProtocolIntegrationTestCase.Context(
            engine, engineDispatcher, engineRunner, engineMessageHandlers,
            aggregatorDispatcher, frontendPublisher, aggregator)

        # not sure why this is necessary. asyncTeardown should be doing this already
        self.addCleanup(lambda : engine.stop())
        await self.start_engine()

    async def asyncTeardown(self) -> None:
        await self.stop()
        await super().asyncTearDown()

    async def start_engine(self):
        assert self.ctx is not None
        self.ctx.engine.run()

    async def stop(self):
        assert self.ctx is not None
        await self.ctx.engineDispatcher.disconnect_async()
        await self.ctx.engineRunner.shutdown()

    async def register(self) -> str:
        assert self.ctx is not None

        register_message = EM.RegisterEngineMsg(
            computer_name="test_host",
            uod_name="test_uod_name",
            uod_author_name="uod-author-name",
            uod_author_email="uod-author-email",
            uod_filename="uod-filename",
            location="test_location",
            engine_version="1")

        register_response = await self.ctx.engineDispatcher.send_registration_msg_async(register_message)
        assert isinstance(register_response, AM.RegisterEngineReplyMsg)
        self.assertTrue(register_response.success)
        engine_id = register_response.engine_id
        assert engine_id is not None
        self.assertTrue(engine_id != "")
        self.assertEqual(self.ctx.engineDispatcher._engine_id, engine_id)
        self.assertTrue(self.ctx.aggregatorDispatcher.has_connected_engine_id(engine_id))
        return engine_id


class ProtocolIntegrationTest(ProtocolIntegrationTestCase):

    async def test_can_register(self):
        assert self.ctx is not None
        engine_id = await self.register()
        self.assertTrue(engine_id != "")

        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        assert engine_data is not None

    async def test_can_send_tag_updates(self):
        assert self.ctx is not None

        with database.create_scope():
            await self.ctx.engineRunner._connect_async()
            while self.ctx.engineRunner.state != "Connected":
                await asyncio.sleep(.5)

        assert self.ctx.engineDispatcher._engine_id is not None

        await asyncio.sleep(1)

        engine_data = self.ctx.aggregator.get_registered_engine_data(self.ctx.engineDispatcher._engine_id)
        assert engine_data is not None
        self.assertEqual(len(engine_data.tags_info.map), len(self.ctx.engine.tags))
        self.assertEqual(engine_data.system_state.value, SystemStateEnum.Stopped)  # type: ignore

    async def test_can_detect_network_down_and_buffer_up_messages(self):
        assert self.ctx is not None
        with database.create_scope():
            await self.ctx.engineRunner._connect_async()

        self.ctx.engineDispatcher.network_failing = True
        self.assertTrue(self.ctx.engineRunner._get_buffer_size() == 0)

        # post message while network_failing==True triggers Failed state
        # and the message is buffered
        await self.ctx.engineRunner._post_async(EM.EngineMessage())

        self.assertEqual(self.ctx.engineRunner.state, "Failed")
        self.assertTrue(self.ctx.engineRunner._get_buffer_size() > 0)


class AggregatorErrorTest(ProtocolIntegrationTestCase):
    async def test_can_get_engine_data_for_registered_engine(self):
        # register engine and check engine_data.connected == True
        assert self.ctx is not None
        engine_id = await self.register()

        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        self.assertIsNotNone(engine_data)

    async def test_rpc_call_fail_with_network_error_engine_state_is_removed(self):
        assert self.ctx is not None

        with database.create_scope():
            await self.ctx.engineRunner._connect_async()
            engine_id = self.ctx.engineDispatcher._engine_id
            assert engine_id is not None

        self.assertTrue(self.ctx.aggregatorDispatcher.has_connected_engine_id(engine_id))

        self.ctx.aggregatorDispatcher.set_engine_fail(engine_id, True)
        try:
            await self.ctx.aggregatorDispatcher.rpc_call(engine_id=engine_id, message=M.MessageBase())
        except Exception:
            pass

        self.assertFalse(self.ctx.aggregatorDispatcher.has_connected_engine_id(engine_id))

        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        self.assertIsNone(engine_data)


class AggregatorTestDispatcher(AggregatorDispatcher):
    def __init__(self) -> None:
        super().__init__()
        self.engineDispatcher: EngineDispatcher
        self.connected_engines: set[str] = set()
        self.failing_engines: set[str] = set()

    def set_engine_fail(self, engine_id: str, failing: bool):
        self.failing_engines.add(engine_id)

    def get_engine_fail(self, engine_id):
        return engine_id in self.failing_engines

    async def rpc_call(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        if self.get_engine_fail(engine_id):
            self.connected_engines.remove(engine_id)
            assert self._disconnect_handler is not None
            await self._disconnect_handler(engine_id)
            raise ProtocolNetworkException()
        if not self.has_connected_engine_id(engine_id):
            raise ProtocolException("Unknown engine: " + engine_id)
        response = await self.engineDispatcher.dispatch_message_async(message)
        assert isinstance(response, M.MessageBase)
        return response

    async def dispatch_message(self, message: EM.EngineMessage) -> M.MessageBase:
        response = await super().dispatch_message(message)
        if isinstance(response, M.ProtocolErrorMessage):
            raise ValueError("Dispatch failed with protocol error: " + str(response.protocol_msg))
        return response

    def has_connected_engine_id(self, engine_id: str) -> bool:
        return engine_id in self.connected_engines

class EngineTestDispatcher(EngineDispatcher):
    def __init__(self) -> None:
        uod_options = {
            'uod_name': 'my_uod_name',
            'uod_author_name': 'my_uod_author_name',
            'uod_author_email': 'my_uod_author_email',
            'uod_filename': 'my_uod_filename',
            'location': 'my_location'
        }
        super().__init__(aggregator_host="", secure=False, uod_options=uod_options)
        self.aggregatorDispatcher: AggregatorTestDispatcher
        self.network_failing = False

    async def connect_async(self):
        if self._engine_id is None:
            logger.info("Registering for engine_id")
            self._engine_id = await self._register_for_engine_id_async()
            if self._engine_id is None:
                logger.error("Failed to register. Aggregator refused registration.")
                raise ValueError("Failed to register. Aggregator refused registration.")

    async def send_registration_msg_async(self, message: EM.RegisterEngineMsg) -> M.MessageBase:
        assert self.aggregatorDispatcher is not None
        assert self.aggregatorDispatcher._register_handler is not None
        result = await self.aggregatorDispatcher._register_handler(message)
        assert isinstance(result, AM.RegisterEngineReplyMsg)
        assert result.engine_id is not None
        self.aggregatorDispatcher.connected_engines.add(result.engine_id)
        self._engine_id = result.engine_id
        return result

    async def send_async(self, message: EM.EngineMessage) -> M.MessageBase:
        # fill in message.engine_id
        if (self._engine_id is None):
            raise Exception("_engine_id should have been set")
        message.engine_id = self._engine_id
        if self.network_failing:
            raise ProtocolNetworkException
        # post message directly to aggregatorDispatcher
        response = await self.aggregatorDispatcher.dispatch_message(message)
        if isinstance(response, AM.RegisterEngineReplyMsg) and response.success:
            self._engine_id = response.engine_id
        return response


class MessageTest(unittest.TestCase):
    def test_print_sequence_range(self):
        self.assertEqual("", EM.print_sequence_range([]))

        m1 = EM.EngineMessage(sequence_number=1)
        self.assertEqual("1", EM.print_sequence_range([m1]))

        m2 = EM.EngineMessage(sequence_number=2)
        m3 = EM.EngineMessage(sequence_number=3)
        self.assertEqual("1-3", EM.print_sequence_range([m1, m2, m3]))
        self.assertEqual("2-3", EM.print_sequence_range([m2, m3]))
        self.assertEqual("1,3", EM.print_sequence_range([m1, m3]))

        m4 = EM.EngineMessage(sequence_number=4)
        m5 = EM.EngineMessage(sequence_number=5)
        self.assertEqual("1-5", EM.print_sequence_range([m1, m2, m3, m4, m5]))
        self.assertEqual("1-2,4-5", EM.print_sequence_range([m1, m2, m4, m5]))
        self.assertEqual("1-3,5", EM.print_sequence_range([m1, m2, m3, m5]))
        self.assertEqual("2,4-5", EM.print_sequence_range([m2, m4, m5]))


if __name__ == "__main__":
    unittest.main()
