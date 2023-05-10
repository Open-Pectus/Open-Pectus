import asyncio
import os
import sys
import unittest
from multiprocessing import Process
import httpx

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_rpc.logger import get_logger
from fastapi_websocket_rpc.utils import gen_uid

from unittest import IsolatedAsyncioTestCase
from fastapi_websocket_pubsub import PubSubClient, PubSubEndpoint
from fastapi_websocket_pubsub.event_notifier import ALL_TOPICS

# Add parent path to use local src as package for tests
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
)

from protocol.aggregator import (
    app as server_app,
    endpoint as server_endpoint,
    server
)
from protocol.engine import create_client


logger = get_logger("Test")

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
    yield proc
    proc.kill()  # Cleanup after test


class AsyncServerTestCase(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        logger.info("asyncSetUp")
        try:
            _ = httpx.get(health_url)
            self.assertFalse(True, "Server should not be running. Test setup failed")
        except Exception:
            pass

        # start server
        self.proc = next(start_server_process())

    async def asyncTearDown(self):
        logger.info("asyncTearDown")
        p = getattr(self, 'proc', None)
        if p is not None:
            assert isinstance(p, Process)
            if p.is_alive():
                logger.error("Server process still running on TearDown - killing it")
                p.kill()


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

        async def on_register():
            logger.info("client registered")
            registered_event.set()

        await client.wait_start_connect(ws_url, ps_client)
        register_success = await client.register(on_register=on_register)
        self.assertTrue(register_success)

        await asyncio.wait_for(registered_event.wait(), 5)

        await ps_client.disconnect()
        await ps_client.wait_until_done()


if __name__ == "__main__":
    unittest.main()
