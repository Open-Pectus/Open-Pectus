from __future__ import annotations
import asyncio
from dataclasses import dataclass
from datetime import timedelta
import logging
import unittest

from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import SystemStateEnum
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_reporter import EngineReporter
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
import openpectus.protocol.aggregator_messages as AM
from openpectus.protocol.engine_dispatcher import EngineDispatcher, EngineDispatcherBase
from openpectus.protocol.engine_dispatcher_error import EngineDispatcherErrorRecoveryDecorator
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
logging.getLogger('openpectus.protocol.engine_dispatcher_error').setLevel(logging.DEBUG)
logging.getLogger('openpectus.engine.engine_reporter').setLevel(logging.DEBUG)
logging.getLogger('openpectus.aggregator.aggregator').setLevel(logging.DEBUG)
logging.getLogger('openpectus.protocol.aggregator_dispatcher').setLevel(logging.DEBUG)


class ProtocolIntegrationTestCase(unittest.IsolatedAsyncioTestCase):

    @dataclass
    class Context:
        """ Test helper class """
        engine: Engine
        engineDispatcher: EngineTestDispatcher
        engineErrorDispatcher: EngineDispatcherErrorRecoveryDecorator
        engineMessageHandlers: EngineMessageHandlers
        engineReporter: EngineReporter

        aggregatorDispatcher: AggregatorTestDispatcher
        frontendPublisher: FrontendPublisher
        aggregator: Aggregator

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.ctx: ProtocolIntegrationTestCase.Context | None = None

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
        engineDispatcher = EngineTestDispatcher(loop)
        engineErrorDispatcher = EngineDispatcherErrorRecoveryDecorator(engineDispatcher)
        engineMessageHandlers = EngineMessageHandlers(engine, engineDispatcher)
        engineReporter = EngineReporter(engine, engineErrorDispatcher)

        aggregatorDispatcher = AggregatorTestDispatcher()
        frontendPublisher = FrontendPublisher()
        aggregator = Aggregator(aggregatorDispatcher, frontendPublisher)
        _ = AggregatorMessageHandlers(aggregator)

        # connect the two test dispatchers for direct communication
        aggregatorDispatcher.engineDispatcher = engineErrorDispatcher
        engineDispatcher.aggregatorDispatcher = aggregatorDispatcher

        self.ctx = ProtocolIntegrationTestCase.Context(
            engine, engineDispatcher, engineErrorDispatcher, engineMessageHandlers, engineReporter,
            aggregatorDispatcher, frontendPublisher, aggregator)

        # not sure why this is necessary. asyncTeardown should be doing this already
        self.addCleanup(lambda : engine.stop())
        await self.start_engine()

    async def asyncTeardown(self) -> None:
        await self.stop_engine()
        await super().asyncTearDown()

    async def start_engine(self):
        assert self.ctx is not None
        self.ctx.engine.run()

    async def stop_engine(self):
        assert self.ctx is not None
        await self.ctx.engineDispatcher.disconnect_async()

    async def register(self) -> str:
        assert self.ctx is not None

        register_message = EM.RegisterEngineMsg(
            computer_name="test_host", uod_name="test_uod_name", location="test_location", engine_version="1")

        register_response = await self.ctx.engineDispatcher.post_async(register_message)
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
        await self.register()

        with database.create_scope():
            await self.ctx.engineReporter.notify_initial_tags()

        assert self.ctx.engineDispatcher._engine_id is not None
        engine_data = self.ctx.aggregator.get_registered_engine_data(self.ctx.engineDispatcher._engine_id)
        assert engine_data is not None
        self.assertEqual(len(engine_data.tags_info.map), len(self.ctx.engine.tags))
        self.assertEqual(engine_data.system_state.value, SystemStateEnum.Stopped)  # type: ignore

    async def test_can_detect_network_down_and_buffer_up_messages(self):
        assert self.ctx is not None
        await self.register()

        with database.create_scope():
            await self.ctx.engineReporter.send_config_messages()
            await self.ctx.engineReporter.send_data_messages()

            self.ctx.engineDispatcher.network_failing = True
            self.ctx.engineErrorDispatcher._buffer_duration = timedelta(seconds=.5)
            self.assertTrue(self.ctx.engineErrorDispatcher._get_buffer_size() == 0)

            # trigger tick()
            await self.ctx.engineReporter.send_data_messages()

            self.assertEqual(self.ctx.engineErrorDispatcher._is_reconnecting, True)
            self.assertTrue(self.ctx.engineErrorDispatcher._get_buffer_size() > 0)

    async def test_can_send_buffered_messages_when_connection_is_restored(self):
        assert self.ctx is not None
        await self.register()

        with database.create_scope():
            await self.ctx.engineReporter.send_config_messages()
            await self.ctx.engineReporter.send_data_messages()

            self.ctx.engineDispatcher.network_failing = True
            self.ctx.engineErrorDispatcher._buffer_duration = timedelta(seconds=.5)
            self.assertTrue(self.ctx.engineErrorDispatcher._get_buffer_size() == 0)
            await self.ctx.engineReporter.send_data_messages()
            self.assertEqual(self.ctx.engineErrorDispatcher._is_reconnecting, True)
            self.assertTrue(self.ctx.engineErrorDispatcher._get_buffer_size() > 0)

            self.ctx.engineDispatcher.network_failing = False
            await self.ctx.engineReporter.send_data_messages()

            self.assertEqual(self.ctx.engineErrorDispatcher._is_reconnecting, False)
            self.assertTrue(self.ctx.engineErrorDispatcher._get_buffer_size() == 0)


    # aggregator must store data, even before a recent run is created. In case it dies and comes back we must have available
    # the engine data from before it went down.

class AggregatorErrorTest(ProtocolIntegrationTestCase):
    async def test_can_get_engine_data_for_registered_engine(self):
        # register engine and check engine_data.connected == True
        assert self.ctx is not None
        engine_id = await self.register()

        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        self.assertIsNotNone(engine_data)

    async def test_rpc_call_fail_with_network_error_engine_state_is_removed(self):
        assert self.ctx is not None
        engine_id = await self.register()

        with database.create_scope():
            await self.ctx.engineReporter.send_uod_info()
            await self.ctx.engineReporter.notify_initial_tags()

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
        self.engineDispatcher: EngineDispatcherBase
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
        response = await self.engineDispatcher._dispatch_message_async(message)
        assert isinstance(response, M.MessageBase)
        return response

    async def dispatch_post(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        response = await super().dispatch_post(message)
        if isinstance(message, EM.RegisterEngineMsg):
            if isinstance(response, AM.RegisterEngineReplyMsg) and response.success:
                assert isinstance(response.engine_id, str)
                assert response.engine_id != ""
                self.connected_engines.add(response.engine_id)
        elif isinstance(response, M.ProtocolErrorMessage):
            raise ValueError("Dispatch failed with protocol error: " + str(response.protocol_msg))
        return response

    def has_connected_engine_id(self, engine_id: str) -> bool:
        return engine_id in self.connected_engines

class EngineTestDispatcher(EngineDispatcher):
    def __init__(self, event_loop: asyncio.AbstractEventLoop) -> None:
        super().__init__(aggregator_host="", uod_name="", location="")
        self.event_loop = event_loop
        self.aggregatorDispatcher: AggregatorTestDispatcher
        self.network_failing = False

    async def connect_async(self):
        if self._engine_id is None:
            logger.info("Registering for engine_id")
            self._engine_id = await self._register_for_engine_id_async(self._uod_name, self._location)
            if self._engine_id is None:
                logger.error("Failed to register. Aggregator refused registration.")
                raise ValueError("Failed to register. Aggregator refused registration.")

    async def post_async(self, message: EM.EngineMessage | EM.RegisterEngineMsg) -> M.MessageBase:
        # fill in message.engine_id
        if (not isinstance(message, EM.RegisterEngineMsg)):  # Special case for registering
            if (self._engine_id is None):
                logger.error("Engine did not have engine_id yet")
                return M.ErrorMessage(message="Engine did not have engine_id yet")
            message.engine_id = self._engine_id
        if self.network_failing:
            raise ProtocolNetworkException
        # post message directly to aggregatorDispatcher
        response = await self.aggregatorDispatcher.dispatch_post(message)
        if isinstance(response, AM.RegisterEngineReplyMsg) and response.success:
            self._engine_id = response.engine_id
        return response


if __name__ == "__main__":
    unittest.main()
