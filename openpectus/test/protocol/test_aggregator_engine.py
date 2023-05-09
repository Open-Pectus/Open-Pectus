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
    app as fastApiApp,
    server
)


logger = get_logger("Test")

PORT = 7990
uri = f"ws://localhost:{PORT}/pubsub"
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


agg_server = None

def setup_server():
    #app = FastAPI()
    print("setup_server")

    #from protocol.aggregator import app  #, server, endpoint
    # global agg_server
    # agg_server = server
    # PubSub websocket endpoint
    #endpoint = PubSubEndpoint()
    #endpoint.register_route(app, path="/pubsub")
    # Regular REST endpoint - that publishes to PubSub
    #setup_server_rest_route(app, endpoint)
    #uvicorn.run(app, port=PORT)
    uvicorn.run(fastApiApp, port=PORT)

def start_server_process():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


class AggregatorServerTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # start server
        next(start_server_process())

    def test_can_start_aggregator(self):
        response = httpx.get(health_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('"healthy"', response.text)

        # self.assertIsNotNone(agg_server)
        # print(f"test_can_start done, client count: {len(agg_server.channel_map)}")


class IntegrationTest(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        next(start_server_process())

    def test_can_start_aggregator(self):
        response = httpx.get(health_url)
        self.assertEqual(200, response.status_code)
        self.assertEqual('"healthy"', response.text)

    async def test_can_register_engine(self):
        self.assertIsNotNone(agg_server)
        pass


if __name__ == "__main__":
    unittest.main()
