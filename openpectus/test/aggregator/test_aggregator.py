import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, AsyncMock

import openpectus.aggregator.data.models as DMdl
import openpectus.aggregator.models as Mdl
import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
from fastapi_websocket_rpc.schemas import RpcResponse
from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher
from openpectus.protocol.models import SystemTagName


class AggregatorTest(unittest.IsolatedAsyncioTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)

    async def create_channel_mock(self, engine_id: str | None):
        response = RpcResponse[str | None](result=engine_id, result_type=None)
        return Mock(close=AsyncMock(), other=Mock(get_engine_id_async=AsyncMock(return_value=response)))

    async def connectRpc(self, dispatcher: AggregatorDispatcher, engine_id: str | None):
        channel = await self.create_channel_mock(engine_id)
        await dispatcher._on_delayed_client_connect(channel)
        return channel

    async def disconnectRpc(self, dispatcher: AggregatorDispatcher, engine_id: str):
        channel = dispatcher._engine_id_channel_map[engine_id]
        await dispatcher.on_client_disconnect(channel)

    def createPublisherMock(self):
        return Mock(
            publish_process_units_changed=AsyncMock(),
            publish_control_state_changed=AsyncMock(),
        )

    async def test_register_engine(self):
        # setup in-memory database
        database.configure_db("sqlite:///:memory:")
        DMdl.DBModel.metadata.create_all(database._engine)  # type: ignore

        dispatcher = AggregatorDispatcher()
        aggregator = Aggregator(dispatcher, self.createPublisherMock(), Mock())
        _ = AggregatorMessageHandlers(aggregator)
        register_engine_msg = EM.RegisterEngineMsg(
            computer_name='computer-name',
            uod_name='uod-name',
            uod_author_name="uod-author-name",
            uod_author_email="uod-author-email",
            uod_filename="uod-filename",
            location="test location",
            engine_version='0.0.1')
        engine_id = aggregator.create_engine_id(register_engine_msg)

        # connecting rpc with no response for engine id should close connection
        channel = await self.connectRpc(dispatcher, None)
        channel.close.assert_called()

        # registering while not registered before should succceed
        assert dispatcher._register_handler is not None
        resultMessage = await dispatcher._register_handler(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, True)

        # connecting rpc now should not close connection
        channel = await self.connectRpc(dispatcher, engine_id)
        channel.close.assert_not_called()

        # registering while already registered and still connected should fail
        resultMessage = await dispatcher._register_handler(register_engine_msg)
        assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
        self.assertEqual(resultMessage.success, False)

        # setup in-memory database - required for engine_disconnected
        database.configure_db("sqlite:///:memory:")
        DMdl.DBModel.metadata.create_all(database._engine)  # type: ignore
        with database.create_scope():
            # registering while already registered, but after disconnect should succeed
            await self.disconnectRpc(dispatcher, engine_id)
            resultMessage = await dispatcher._register_handler(register_engine_msg)
            assert isinstance(resultMessage, AM.RegisterEngineReplyMsg)
            self.assertEqual(resultMessage.success, True)

    async def test_register_engine_different_name(self):
        # setup in-memory database
        database.configure_db("sqlite:///:memory:")
        DMdl.DBModel.metadata.create_all(database._engine)  # type: ignore

        dispatcher = AggregatorDispatcher()
        aggregator = Aggregator(dispatcher, self.createPublisherMock(), Mock())
        messageHandlers = AggregatorMessageHandlers(aggregator)
        register_engine_msg = EM.RegisterEngineMsg(
            computer_name='computer-name',
            uod_name='uod-name',
            uod_author_name="uod-author-name",
            uod_author_email="uod-author-email",
            uod_filename="uod-filename",
            location="test-loc",
            engine_version='0.0.1')
        register_engine_msg_different_computer = EM.RegisterEngineMsg(
            computer_name='computer-name2',
            uod_name='uod-name',
            uod_author_name="uod-author-name",
            uod_author_email="uod-author-email",
            uod_filename="uod-filename",
            location="test-loc",
            engine_version='0.0.1')
        engine_id1 = aggregator.create_engine_id(register_engine_msg)
        _ = aggregator.create_engine_id(register_engine_msg_different_computer)

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

class AggregatorEventsTest(unittest.IsolatedAsyncioTestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.stored_tags = []
        self.plot_log_repo = Mock(store_tag_values=self.store_tag_values)
        self.aggregator = Aggregator(Mock(), Mock(), Mock())
        self.engine_data = Mdl.EngineData(
            engine_id="test_engine", computer_name="", engine_version="", hardware_str="",
            uod_name="", uod_author_name="", uod_author_email="", uod_filename="", location="",
            data_log_interval_seconds=5
        )

    def createTag(self, name: str, tick: float, value: str):
        return Mdl.TagValue(name=name, tick_time=tick, value=value, value_formatted=None, value_unit=None)

    def store_tag_values(self, engine_id: str, run_id: str, tags: list[Mdl.TagValue]):
        self.stored_tags.extend(tags)

    def process_tags(self, tags: list[Mdl.TagValue]):
        for tag in tags:
            self.engine_data.tags_info.upsert(tag)


    async def test_persist_tag_values_can_save_new_tags(self):
        run_id = self.createTag(SystemTagName.RUN_ID.value, 1, "run1")
        tags = [
            run_id,
            self.createTag("a", 1, "v1"),
            self.createTag("b", 1, "v1"),
        ]
        self.process_tags(tags)

        # create run_data to simulate a started run
        self.engine_data.run_data = Mdl.RunData.empty(run_id="run1", run_started=datetime.now(timezone.utc))

        self.aggregator.from_engine._persist_tag_values(self.engine_data, self.plot_log_repo)

        self.assertEqual(tags, self.stored_tags)

    async def test_persist_tag_values_can_update_tag_with_newer_after_threshold(self):
        run_id = self.createTag(SystemTagName.RUN_ID.value, 1, "run1")

        tags = [
            run_id,
            self.createTag("a", 1, "v1"),
            self.createTag("b", 1, "v1"),
        ]
        self.process_tags(tags)

        # create run_data to simulate a started run
        self.engine_data.run_data = Mdl.RunData.empty(run_id="run1", run_started=datetime.now(timezone.utc))

        self.aggregator.from_engine._persist_tag_values(self.engine_data, self.plot_log_repo)
        self.stored_tags.clear()

        # data newer but not beyond threshold is not saved
        tmp_tags = [
            self.createTag("a", 1.1 + 3, "v2"),  # threshold is 5 seconds
        ]
        self.process_tags(tmp_tags)
        self.aggregator.from_engine._persist_tag_values(self.engine_data, self.plot_log_repo)

        self.assertEqual([], self.stored_tags)

        # data newer and beyond threshold is saved
        new_tags = [
            self.createTag("a", 1.1 + 5, "v2"),  # threshold is 5 seconds
        ]
        self.process_tags(new_tags)
        self.aggregator.from_engine._persist_tag_values(self.engine_data, self.plot_log_repo)

        self.assertEqual(new_tags, self.stored_tags)

    async def test_persist_tag_values_cannot_update_tag_with_older(self):
        run_id = self.createTag(SystemTagName.RUN_ID.value, 1, "run1")
        tags = [
            run_id,
            self.createTag("a", 2, "v1"),
            self.createTag("b", 2, "v1"),
        ]
        self.process_tags(tags)

        # create run_data to simulate a started run
        self.engine_data.run_data = Mdl.RunData.empty(run_id="run1", run_started=datetime.now(timezone.utc))

        self.aggregator.from_engine._persist_tag_values(self.engine_data, self.plot_log_repo)
        self.stored_tags.clear()
        self.assertEqual(2, self.engine_data.run_data.latest_persisted_tick_time)

        new_tags = [
            self.createTag("a", 1, "v2"),
        ]

        # So we allow this to update the tag value with an older time and give a warning
        # - but we disallow persisting this older value??
        self.process_tags(new_tags)

        self.aggregator.from_engine._persist_tag_values(self.engine_data, self.plot_log_repo)

        self.assertEqual([], self.stored_tags)


if __name__ == '__main__':
    unittest.main()
