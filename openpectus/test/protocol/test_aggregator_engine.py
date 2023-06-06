import asyncio
import logging
import os
import sys
import unittest
from multiprocessing import Process
import httpx

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_rpc.logger import get_logger

from unittest import IsolatedAsyncioTestCase
from fastapi_websocket_pubsub import PubSubClient, PubSubEndpoint
from protocol.messages import (
    RegisterEngineMsg,
    SuccessMessage,
    TagValue,
    TagsUpdatedMsg,
    serialize_msg_to_json,
    deserialize_msg_from_json
)

# Add parent path to use local src as package for tests
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from protocol.aggregator import (
    app as server_app,
    endpoint as server_endpoint
)
from protocol.engine import create_client

logging.basicConfig()
logger = get_logger("Test")
logger.setLevel(logging.DEBUG)

PORT = 7990
ws_url = f"ws://localhost:{PORT}/pubsub"
trigger_url = f"http://localhost:{PORT}/trigger"
health_url = f"http://localhost:{PORT}/health"

DATA = "MAGIC"
EVENT_TOPIC = "event/has-happened"


def setup_server_rest_route(app: FastAPI, endpoint: PubSubEndpoint):
    @app.get("/trigger")
    async def trigger_events():
        logger.info("Triggered via HTTP route - publishing event")
        # Publish an event named 'steel'
        # Since we are calling back (RPC) to the client- this would deadlock if we wait on it
        asyncio.create_task(endpoint.publish([EVENT_TOPIC], data=DATA))
        return "triggered"


def setup_server():
    # Regular REST endpoint - that publishes to PubSub
    setup_server_rest_route(server_app, server_endpoint)
    uvicorn.run(server_app, port=PORT)


def start_server_process():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    return proc


class AsyncServerTestCase(IsolatedAsyncioTestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.proc : Process | None = None

    async def asyncSetUp(self):
        logger.info("asyncSetUp")
        try:
            _ = httpx.get(health_url)
            self.assertFalse(True, "Server should not be running. Test setup failed")
        except httpx.ConnectError:
            pass

        await asyncio.sleep(.05)

        self.proc = start_server_process()

    async def asyncTearDown(self):
        logger.info("asyncTearDown")

        if self.proc is not None:
            if self.proc.is_alive():
                logger.debug("Server process still running on TearDown - killing it")
                self.proc.kill()


class IntegrationTest(AsyncServerTestCase):

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

            ps_client.subscribe(EVENT_TOPIC, on_event)
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

        client, ps_client = create_client(on_connect_callback=on_connect)
        ps_client.start_client(ws_url)
        self.assertFalse(client.connected)
        await ps_client.wait_until_ready()

        await asyncio.wait_for(connected_event.wait(), 5)

        self.assertTrue(client.connected)
        await ps_client.disconnect()
        await ps_client.wait_until_done()

    async def test_can_connect_client_simple(self):

        client, ps_client = create_client()
        await client.wait_start_connect(ws_url, ps_client)

        self.assertTrue(client.connected)
        await ps_client.disconnect()
        await ps_client.wait_until_done()

    async def test_can_register_client(self):
        client, ps_client = create_client()

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

        await client.wait_start_connect(ws_url, ps_client)
        msg = RegisterEngineMsg(engine_name="test-eng", uod_name="test-uod")
        register_success = await client.send(msg, on_success=on_register, on_error=on_error)
        self.assertTrue(register_success)

        await asyncio.wait_for(registered_event.wait(), 5)
        self.assertTrue(client_registered)
        self.assertFalse(client_failed)

        await ps_client.disconnect()
        await ps_client.wait_until_done()

    async def test_client_can_send_message(self):
        client, ps_client = create_client()

        await client.wait_start_connect(ws_url, ps_client)
        msg = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar")])
        result = await client.send(msg)
        self.assertIsInstance(result, SuccessMessage)

        await ps_client.disconnect()
        await ps_client.wait_until_done()


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
        self.assertEqual(reg.engine_name, reg_d.engine_name)
        self.assertEqual(reg.uod_name, reg_d.uod_name)

    def test_serialization_TagsUpdatedMsg(self):        
        tu = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar")])
        tu_s = serialize_msg_to_json(tu)
        self.assertIsNotNone(tu_s)

    def test_round_trip_TagsUpdatedMsg(self):
        tu = TagsUpdatedMsg(tags=[TagValue(name="foo", value="bar")])
        tu_s = serialize_msg_to_json(tu)
        self.assertIsNotNone(tu_s)

        tu_d = deserialize_msg_from_json(tu_s)
        self.assertIsNotNone(tu_d)
        self.assertIsInstance(tu_d, TagsUpdatedMsg)
        self.assertEqual(tu_d.tags[0].name, tu.tags[0].name)


if __name__ == "__main__":
    unittest.main()
