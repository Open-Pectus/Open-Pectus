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


class AggregatorServerTest(AsyncServerTestCase):

    def test_can_start_aggregator(self):
        response = httpx.get(health_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('"healthy"', response.text)

        # self.assertIsNotNone(agg_server)
        # print(f"test_can_start done, client count: {len(agg_server.channel_map)}")


class IntegrationTest(AsyncServerTestCase):

    def test_can_start_server(self):
        response = httpx.get(health_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('"healthy"', response.text)

    # async def test_can_register_engine(self):
    #     self.assertIsNotNone(server)
    #     pass

    async def test_can_connect_client(self):

        client, ps_client = create_client()
        ps_client.start_client(ws_url)
        self.assertFalse(client.connected)
        await ps_client.wait_until_ready()

        # FIXME - maybe we'll need a local handler where we can set a finish event
        await asyncio.sleep(.1)

        self.assertTrue(client.connected)
        # print(f"client.connected 1: {client.connected}")
        await ps_client.disconnect()
        # print(f"client.connected 2: {client.connected}")
        await ps_client.wait_until_done()
        # print(f"client.connected 3: {client.connected}")

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


if __name__ == "__main__":
    unittest.main()
