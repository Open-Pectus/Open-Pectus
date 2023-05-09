import asyncio
import os
import sys
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase
import httpx

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_pubsub import PubSubClient, PubSubEndpoint
from fastapi_websocket_rpc.logger import get_logger
from fastapi_websocket_rpc.utils import gen_uid

# Add parent path to use local src as package for tests
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
)

logger = get_logger("Test")

PORT = 7990
uri = f"ws://localhost:{PORT}/pubsub"
trigger_url = f"http://localhost:{PORT}/trigger"

DATA = "MAGIC"
EVENT_TOPIC = "event/has-happened"


def setup_server_rest_route(app, endpoint: PubSubEndpoint):
    @app.get("/trigger")
    async def trigger_events():
        logger.info("Triggered via HTTP route - publishing event")
        # Publish an event named 'steel'
        # Since we are calling back (RPC) to the client- this would deadlock if we wait on it
        asyncio.create_task(endpoint.publish([EVENT_TOPIC], data=DATA))
        return "triggered"


def setup_server():
    app = FastAPI()
    # PubSub websocket endpoint
    endpoint = PubSubEndpoint()
    endpoint.register_route(app, path="/pubsub")
    # Regular REST endpoint - that publishes to PubSub
    setup_server_rest_route(app, endpoint)
    uvicorn.run(app, port=PORT)


def server():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


class TestPubSub(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        next(server())

    async def test_pub_sub(self):
        # finish trigger
        finish = asyncio.Event()

        # Create a client and subscribe to topics
        async with PubSubClient() as client:

            async def on_event(data, topic):
                assert data == DATA
                print("event received with data: " + data)
                finish.set()

            # subscribe for the event
            client.subscribe(EVENT_TOPIC, on_event)
            # start listentining
            client.start_client(uri)
            # wait for the client to be ready to receive events
            await client.wait_until_ready()
            # publish events (with sync=False to avoid deadlocks waiting on the publish to ourselves)
            published = await client.publish(
                [EVENT_TOPIC], data=DATA, sync=False, notifier_id=gen_uid()
            )
            assert published.result
            # wait for finish trigger
            await asyncio.wait_for(finish.wait(), 5)

    async def test_pub_sub_two_clients(self):
        # finish trigger
        finish = asyncio.Event()

        # Create a client and subscribe to topics
        async with PubSubClient() as client, PubSubClient() as client2:
            received_data = None

            async def on_event(data, topic):
                nonlocal received_data
                received_data = data
                finish.set()

            client.subscribe(EVENT_TOPIC, on_event)
            client.start_client(uri)
            await client.wait_until_ready()
            
            client2.start_client(uri)
            await client2.wait_until_ready()

            # publish events (with sync=False to avoid deadlocks waiting on the publish to ourselves)
            published = await client2.publish(
                [EVENT_TOPIC], data=DATA, sync=False, notifier_id=gen_uid()
            )
            self.assertTrue(published.result)
            # wait for finish trigger
            await asyncio.wait_for(finish.wait(), 5)

            self.assertEqual(received_data, DATA)

    async def test_rest_trigger(self):
        finish = asyncio.Event()

        async with PubSubClient() as client:
            async def on_event(data, topic):
                self.assertEqual(data, DATA)
                finish.set()

            client.subscribe(EVENT_TOPIC, on_event)
            client.start_client(uri)
            await client.wait_until_ready()

            # trigger publish via rest call
            response = httpx.get(trigger_url)
            self.assertEqual(200, response.status_code)

            # wait for finish trigger
            await asyncio.wait_for(finish.wait(), 5)


if __name__ == "__main__":
    unittest.main()
