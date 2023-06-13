import asyncio
import logging
import os
import sys
import time
import unittest
from multiprocessing import Process
import httpx
import uvicorn
from fastapi import Depends, FastAPI
from fastapi.responses import Response, PlainTextResponse
from fastapi_websocket_rpc.logger import get_logger

# Add parent path to use local src as package for tests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from unittest import IsolatedAsyncioTestCase
from fastapi_websocket_pubsub import PubSubClient, PubSubEndpoint
from protocol.messages import (
    MessageBase,
    RegisterEngineMsg,
    SuccessMessage,
    ErrorMessage,
    TagValue,
    TagsUpdatedMsg,
    InvokeCommandMsg,
    serialize_msg_to_json,
    deserialize_msg_from_json
)

from protocol.aggregator import Aggregator, TagsInfo
import aggregator.deps as agg_deps
from protocol.engine import create_client, Client
from aggregator.routers import aggregator_websocket


server_app = FastAPI()
router = aggregator_websocket.router


logging.basicConfig()
logger = get_logger("Test")
logger.setLevel(logging.DEBUG)

PORT = 7990
ws_url = f"ws://localhost:{PORT}/pubsub"
trigger_url = f"http://localhost:{PORT}/trigger"
trigger_send_url = f"http://localhost:{PORT}/trigger_send"
health_url = f"http://localhost:{PORT}/health"
debug_channels_url = f"http://localhost:{PORT}/debug_channels"
tags_url = f"http://localhost:{PORT}/tags"
clear_state_url = f"http://localhost:{PORT}/clear_state"

DATA = "MAGIC"
EVENT_TOPIC = "event/has-happened"


def setup_server_rest_routes(app: FastAPI, endpoint: PubSubEndpoint):
    @app.get("/trigger")
    async def trigger_events():
        logger.info("Triggered via HTTP route - publishing event")
        # Publish an event named 'steel'
        # Since we are calling back (RPC) to the client- this would deadlock if we wait on it
        asyncio.create_task(endpoint.publish([EVENT_TOPIC], data=DATA))
        return "triggered"

    class SimpleCommandToClient(MessageBase):
        client_id: str
        cmd_name: str

    @app.post("/trigger_send")
    async def trigger_send_command(cmd: SimpleCommandToClient, aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
        if cmd.client_id is None or cmd.client_id == "" or cmd.cmd_name is None or cmd.cmd_name == "":
            return Response("Bad command", status_code=400)

        logger.debug("trigger_send command: " + cmd.cmd_name)
        # can't await this call or the test would deadlock so we fire'n'forget it
        msg = InvokeCommandMsg(name=cmd.cmd_name)
        asyncio.create_task(aggregator.send_to_client(cmd.client_id, msg))
        return PlainTextResponse("OK")

    @app.get("/tags/{client_id}")
    async def tags(client_id: str, aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
        tags = aggregator.get_client_tags(client_id)
        print("tags", tags)
        if tags is None:
            return Response("No tags found for client_id " + client_id, status_code=400)
        return tags

    @app.get("/debug_channels")
    async def debug_channels(aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
        print("Server channel map (channel, ch. closed, client_id, status):")
        for x in aggregator.channel_map.values():
            print(f"{x.channel.id}\t{x.channel.isClosed()}\t{x.client_id}\t{x.status}")

    @app.get("/clear_state")
    async def clear_state(aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
        logger.info("/clear_state")
        aggregator.channel_map.clear()
        aggregator.tags_map.clear()


def setup_server():
    aggregator = agg_deps.create_aggregator(router)
    server_app.include_router(router)
    assert aggregator.endpoint is not None
    # Regular REST endpoint - that publishes to PubSub
    setup_server_rest_routes(server_app, aggregator.endpoint)    
    uvicorn.run(server_app, port=PORT)


def start_server_process():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True, name="uvicorn unit test server")
    proc.start()
    return proc


def send_message_to_client(client_id: str, msg: InvokeCommandMsg):
    """ Use server http test interface ot have it send a message to the given client using its websocket protocol """
    # we do not support args at this time
    response = httpx.post(trigger_send_url,  json={'client_id': client_id, 'cmd_name': msg.name})
    if not response.is_success:
        print("Error response text", response.text)
        raise Exception(f"Server returned non-success status code: {response.status_code}")


def make_server_print_channels():
    response = httpx.get(debug_channels_url)
    if not response.is_success:
        print("Error response text", response.text)
        raise Exception(f"Server returned non-success status code: {response.status_code}")


class AsyncServerTestCase(IsolatedAsyncioTestCase):
    # Note: This test class is not rock solid. When things go wrong, it may leave
    # a server running so a new test run fails. Especially when used with VS Code
    # and a test run is stopped manually. So sometimes a VS Code restart is necessary.

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.proc : Process | None = None
        self.client: Client | None = None

    async def asyncSetUp(self):
        logger.info("asyncSetUp")
        try:
            _ = httpx.get(health_url)

            logger.error("Server running on asyncSetUp. Clearing its state.")
            _ = httpx.get(clear_state_url)

            time.sleep(2)

        except httpx.ConnectError:
            pass

        self.proc = start_server_process()

    async def asyncTearDown(self):
        logger.info("asyncTearDown")

        # handle failed tests that may have left their client connected
        if self.client is not None and self.client.connected:
            try:
                logger.debug("Disconnecting client")
                await self.client.disconnect_wait_async()
            except Exception:
                logger.error("Failed to disconnect client", exc_info=True)
                pass

        try:
            _ = httpx.get(clear_state_url)
        except Exception:
            pass

        if self.proc is not None:
            if self.proc.is_alive():
                logger.debug("Server process still running on TearDown - killing it")
                self.proc.kill()


class IntegrationTest(AsyncServerTestCase):

    def create_test_client(self, on_connect_callback=None) -> Client:
        self.client = create_client(on_connect_callback=on_connect_callback)
        return self.client

    def test_can_start_server(self):
        response = httpx.get(health_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('"healthy"', response.text)

    async def test_can_connect_ps_client(self):
        finish = asyncio.Event()

        async with PubSubClient() as ps_client:
            async def on_event(data, topic):
                self.assertEqual(data, DATA)
                finish.set()

            ps_client.subscribe(EVENT_TOPIC, on_event)  # type: ignore
            ps_client.start_client(ws_url)
            await ps_client.wait_until_ready()

            # trigger publish via rest call
            response = httpx.get(trigger_url)
            self.assertEqual(200, response.status_code)

            # wait for finish trigger
            await asyncio.wait_for(finish.wait(), 5)

    async def test_can_connect_client(self):
        connected_event = asyncio.Event()

        async def on_connect(x, y):
            logger.info("client connected")
            connected_event.set()
            await asyncio.sleep(.1)  # not strictly necessary but yields a warning if no await

        client = self.create_test_client(on_connect_callback=on_connect)
        assert client.ps_client is not None
        client.ps_client.start_client(ws_url)
        self.assertFalse(client.connected)
        await client.ps_client.wait_until_ready()

        await asyncio.wait_for(connected_event.wait(), 5)

        self.assertTrue(client.connected)
        await client.ps_client.disconnect()
        await client.ps_client.wait_until_done()

    async def test_can_connect_client_simple(self):
        client = self.create_test_client()
        await client.start_connect_wait_async(ws_url)

        self.assertTrue(client.connected)
        await client.disconnect_wait_async()

    async def test_can_register_client(self):
        client = self.create_test_client()

        registered_event = asyncio.Event()
        client_registered = False
        client_failed = False

        def on_register():
            logger.info("client registered")
            nonlocal client_registered
            client_registered = True
            registered_event.set()

        def on_error(ex: Exception | None = None):
            nonlocal client_failed
            client_failed = True
            logger.error("Error sending: " + str(ex))

        await client.start_connect_wait_async(ws_url)
        msg = RegisterEngineMsg(engine_name="test-eng", uod_name="test-uod")
        resp_msg = await client.send_to_server(msg, on_success=on_register, on_error=on_error)
        self.assertIsInstance(resp_msg, SuccessMessage)

        await asyncio.wait_for(registered_event.wait(), 5)
        self.assertTrue(client_registered)
        self.assertFalse(client_failed)

        await client.disconnect_wait_async()

    async def test_client_can_send_message(self):
        client = self.create_test_client()

        await client.start_connect_wait_async(ws_url)
        msg = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar", value_unit=None)])
        result = await client.send_to_server(msg)
        self.assertIsInstance(result, ErrorMessage)
        self.assertEqual(result.message, "Client not registered")  # type: ignore

        await client.disconnect_wait_async()

    async def test_can_send_command_trigger(self):
        cmd_msg = InvokeCommandMsg(name="START")
        send_message_to_client(client_id="foo", msg=cmd_msg)

    async def test_client_can_receive_server_message(self):
        client = self.create_test_client()
        await client.start_connect_wait_async(ws_url)
        register_msg = RegisterEngineMsg(engine_name="test-eng", uod_name="test-uod")
        resp_msg = await client.send_to_server(register_msg)
        self.assertIsInstance(resp_msg, SuccessMessage)

        event = asyncio.Event()

        async def on_invoke_command(msg: MessageBase) -> MessageBase:
            # print("on_invoke_command")
            event.set()
            return SuccessMessage()

        client.set_message_handler("InvokeCommandMsg", on_invoke_command)

        # trigger server sent command via rest call
        cmd_msg = InvokeCommandMsg(name="START")
        client_id = Aggregator.get_client_id(register_msg)
        send_message_to_client(client_id, msg=cmd_msg)

        await asyncio.wait_for(event.wait(), 5)

    async def test_server_can_receive_tag_update(self):
        client = self.create_test_client()
        await client.start_connect_wait_async(ws_url)
        register_msg = RegisterEngineMsg(engine_name="eng", uod_name="uod")
        await client.send_to_server(register_msg)

        make_server_print_channels()

        client_id = Aggregator.get_client_id(register_msg)
        msg = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar", value_unit=None)])
        result = await client.send_to_server(msg)
        self.assertIsInstance(result, SuccessMessage)

        response = httpx.get(tags_url + "/" + client_id)
        self.assertEqual(200, response.status_code)

        tags = TagsInfo.parse_raw(response.content)
        self.assertIsNotNone(tags)
        tag = tags.get("foo")
        self.assertIsNotNone(tag)
        self.assertEqual(tag.name, "foo")  # type: ignore
        self.assertEqual(tag.value, "bar")  # type: ignore

        await client.disconnect_wait_async()


class SerializationTest(unittest.TestCase):
    def test_serialization_RegisterEngineMsg(self):
        reg = RegisterEngineMsg(engine_name="foo", uod_name="bar")
        reg_s = serialize_msg_to_json(reg)
        self.assertIsNotNone(reg_s)        

    def test_round_trip_RegisterEngineMsg(self):
        reg = RegisterEngineMsg(engine_name="foo", uod_name="bar")
        reg_s = serialize_msg_to_json(reg)
        reg_d = deserialize_msg_from_json(reg_s)
        self.assertIsNotNone(reg_d)
        self.assertIsInstance(reg_d, RegisterEngineMsg)
        self.assertEqual(reg.engine_name, reg_d.engine_name)  # type: ignore
        self.assertEqual(reg.uod_name, reg_d.uod_name)  # type: ignore

    def test_serialization_TagsUpdatedMsg(self):        
        tu = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar", value_unit="m")])
        tu_s = serialize_msg_to_json(tu)
        self.assertIsNotNone(tu_s)

    def test_round_trip_TagsUpdatedMsg(self):
        tu = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar", value_unit=None)])
        tu_s = serialize_msg_to_json(tu)
        self.assertIsNotNone(tu_s)

        tu_d = deserialize_msg_from_json(tu_s)
        self.assertIsNotNone(tu_d)
        self.assertIsInstance(tu_d, TagsUpdatedMsg)
        self.assertEqual(tu_d.tags[0].name, tu.tags[0].name)  # type: ignore


if __name__ == "__main__":
    unittest.main()
