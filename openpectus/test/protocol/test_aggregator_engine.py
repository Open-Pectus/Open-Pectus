from __future__ import annotations
import asyncio
from dataclasses import dataclass
import logging
from typing import Any, Awaitable, Callable
import unittest

from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.models import SystemStateEnum
from openpectus.engine.engine import Engine
from openpectus.engine.engine_message_handlers import EngineMessageHandlers
from openpectus.engine.engine_reporter import EngineReporter
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcherBase
import openpectus.protocol.aggregator_messages as AM
from openpectus.protocol.engine_dispatcher import EngineDispatcherBase
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
logging.getLogger('openpectus.engine.engine_reporter').setLevel(logging.DEBUG)
logging.getLogger('openpectus.aggregator.aggregator').setLevel(logging.DEBUG)
logging.getLogger('openpectus.protocol.aggregator_dispatcher').setLevel(logging.DEBUG)


class ProtocolIntegrationTestCase(unittest.IsolatedAsyncioTestCase):

    @dataclass
    class Context:
        engine: Engine
        engineDispatcher: EngineTestDispatcher
        engineMessageHandlers: EngineMessageHandlers
        engineReporter: EngineReporter

        aggregatorDispatcher: AggregatorTestDispatcher
        frontendPublisher: FrontendPublisher
        aggregator: Aggregator

    def log(self, s):
        print("*** ProtocolIntegrationTestCase " + s)


    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.ctx: ProtocolIntegrationTestCase.Context | None = None
        self.log("ctor")

    async def asyncSetUp(self) -> None:
        assert self.ctx is None
        await super().asyncSetUp()
        self.log("asyncSetUp")

        # setup in-memory database
        database.configure_db("sqlite:///:memory:")
        DMdl.DBModel.metadata.create_all(database._engine)  # type: ignore

        # the test class IsolatedAsyncioTestCase provides the event loop
        loop = asyncio.get_running_loop()

        uod = create_test_uod()
        engine = Engine(uod)
        engineDispatcher = EngineTestDispatcher(loop)
        engineMessageHandlers = EngineMessageHandlers(engine, engineDispatcher)
        engineReporter = EngineReporter(engine, engineDispatcher)

        aggregatorDispatcher = AggregatorTestDispatcher()
        frontendPublisher = FrontendPublisher()
        aggregator = Aggregator(aggregatorDispatcher, frontendPublisher)
        _ = AggregatorMessageHandlers(aggregator)

        # connect the two test dispatchers for direct commonication
        aggregatorDispatcher.engineDispatcher = engineDispatcher
        engineDispatcher.aggregatorDispatcher = aggregatorDispatcher

        self.ctx = ProtocolIntegrationTestCase.Context(
            engine, engineDispatcher, engineMessageHandlers, engineReporter,
            aggregatorDispatcher, frontendPublisher, aggregator)

        # not sure why this is necessary. asyncTeardown should be doing this already
        self.addCleanup(lambda : engine.stop())

    async def asyncTeardown(self) -> None:
        await self.stop_engine()
        await super().asyncTearDown()

        self.log("asyncTearDown")


    async def start_engine(self):
        assert self.ctx is not None
        #await self.engineReporter.run_loop_async()

    async def stop_engine(self):
        assert self.ctx is not None
        await self.ctx.engineReporter.stop_async()

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


    # aggregator must store data, even before a recent run is created. In case it dies and comes back we must have available
    # the engine data from before it went down.

class AggregatorErrorTest(ProtocolIntegrationTestCase):
    async def test_default_state_is_connected(self):
        # register engine and check engine_data.connected == True
        assert self.ctx is not None
        engine_id = await self.register()

#        with database.create_scope():
#            ...
#            self.ctx.engineReporter.send_uod_info()
#            self.ctx.engineReporter.notify_initial_tags()

        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        assert engine_data is not None

        self.assertEqual(engine_data.connection_faulty, False)

    async def test_rpc_call_fail_with_network_exception_state_is_disconnected(self):
        # register engine and check engine_data.connected == True
        # make rpc_call fail and check engine_data.connected == False

        assert self.ctx is not None
        engine_id = await self.register()

        with database.create_scope():
            await self.ctx.engineReporter.send_uod_info()
            await self.ctx.engineReporter.notify_initial_tags()

        self.ctx.aggregatorDispatcher.set_engine_fail(engine_id, True)
        await self.ctx.aggregatorDispatcher.rpc_call(engine_id=engine_id, message=M.MessageBase())

        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        assert engine_data is not None

        self.assertEqual(engine_data.connection_faulty, True)


    async def test_if_aggregator_gets_no_data_before_timeout_state_is_disconnected(self):
        assert self.ctx is not None
        engine_id = await self.register()
        self.ctx.aggregatorDispatcher.connection_fault_timeout_seconds = 0.5

        with database.create_scope():
            await self.ctx.engineReporter.send_uod_info()
            await self.ctx.engineReporter.notify_initial_tags()

        # wait longer than timeout
        await asyncio.sleep(1.2)

        # we need to add a timer thread to AggregatorDispatcher for this to work
        # - or add the timer in aggregator and add a tick() method in AggregatorDispatcher
        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        assert engine_data is not None
        self.assertEqual(engine_data.connection_faulty, True)

    async def test_if_aggregator_gets_data_before_timeout_state_is_not_disconnected(self):
        assert self.ctx is not None
        engine_id = await self.register()
        self.ctx.aggregatorDispatcher.connection_fault_timeout_seconds = 1.0

        with database.create_scope():
            await self.ctx.engineReporter.send_uod_info()
            await self.ctx.engineReporter.notify_initial_tags()

        # wait longer than timeout
        await asyncio.sleep(0.5)
        await self.ctx.engineReporter.send_runlog()
        await asyncio.sleep(0.5)
        await self.ctx.engineReporter.send_runlog()
        await asyncio.sleep(0.5)

        # we need to add a timer thread to AggregatorDispatcher for this to work
        # - or add the timer in aggregator and add a tick() method in AggregatorDispatcher
        engine_data = self.ctx.aggregator.get_registered_engine_data(engine_id)
        assert engine_data is not None
        self.assertEqual(engine_data.connection_faulty, False)



class AggregatorTestDispatcher(AggregatorDispatcherBase):
    def __init__(self) -> None:
        super().__init__()
        self._handlers: dict[type, Callable[[Any], Awaitable[M.MessageBase]]] = {}        
        self.engineDispatcher: EngineTestDispatcher
        self._engine_connection_failure: dict[str, bool] = {}

    def set_engine_fail(self, engine_id: str, failing: bool):
        self._engine_connection_failure[engine_id] = failing

    def get_engine_fail(self, engine_id):
        return self._engine_connection_failure.get(engine_id, False)

    async def rpc_call_impl(self, engine_id: str, message: M.MessageBase) -> M.MessageBase:
        if self.get_engine_fail(engine_id):
            raise ProtocolNetworkException
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
                self._set_connection_ok(engine_id=response.engine_id)
        elif isinstance(response, M.ProtocolErrorMessage):
            raise ValueError("Dispatch failed with protocol error: " + str(response.protocol_msg))
        return response

class EngineTestDispatcher(EngineDispatcherBase):
    def __init__(self, event_loop: asyncio.AbstractEventLoop) -> None:
        super().__init__()
        self.event_loop = event_loop
        self.aggregatorDispatcher: AggregatorTestDispatcher
        self.network_failing = False

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
