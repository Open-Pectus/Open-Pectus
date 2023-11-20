import asyncio
import unittest
from multiprocessing import Process
from unittest import IsolatedAsyncioTestCase
import httpx

import uvicorn
from fastapi import FastAPI
from fastapi_websocket_pubsub import PubSubClient, PubSubEndpoint
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods, RpcEventClientMethods
from fastapi_websocket_rpc import RpcChannel
from fastapi_websocket_rpc.schemas import RpcResponse
from fastapi_websocket_rpc.logger import get_logger
from fastapi_websocket_rpc.utils import gen_uid


logger = get_logger("Test")

PORT = 7996
ws_url = f"ws://localhost:{PORT}/engine-pubsub"
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


class TestServerRpcMethods(RpcEventServerMethods):
    async def to_upper(self, x: str) -> str:
        await asyncio.sleep(0.1)
        return x.upper()


class TestClientRpcMethods(RpcEventClientMethods):
    async def to_upper(self, x: str) -> str:
        await asyncio.sleep(0.1)
        return x.upper()


def setup_server():
    app = FastAPI()
    # PubSub websocket endpoint
    endpoint = PubSubEndpoint(methods_class=TestServerRpcMethods)
    endpoint.register_route(app, path="/engine-pubsub")
    # Regular REST endpoint - that publishes to PubSub
    setup_server_rest_route(app, endpoint)
    uvicorn.run(app, port=PORT)


def server():
    # Run the server as a separate process
    proc = Process(target=setup_server, args=(), daemon=True)
    proc.start()
    yield proc
    proc.kill()  # Cleanup after test


@unittest.skip("TODO fix on CI build")
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
            client.subscribe(EVENT_TOPIC, on_event)  # type: ignore
            # start listentining
            client.start_client(ws_url)
            # wait for the client to be ready to receive events
            await client.wait_until_ready()
            # publish events (with sync=False to avoid deadlocks waiting on the publish to ourselves)
            published = await client.publish(
                [EVENT_TOPIC], data=DATA, sync=False, notifier_id=gen_uid()
            )
            assert published.result  # type: ignore
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

            client.subscribe(EVENT_TOPIC, on_event)  # type: ignore
            client.start_client(ws_url)
            await client.wait_until_ready()

            client2.start_client(ws_url)
            await client2.wait_until_ready()

            # publish events (with sync=False to avoid deadlocks waiting on the publish to ourselves)
            published = await client2.publish(
                [EVENT_TOPIC], data=DATA, sync=False, notifier_id=gen_uid()
            )
            self.assertTrue(published.result)  # type: ignore
            # wait for finish trigger
            await asyncio.wait_for(finish.wait(), 5)

            self.assertEqual(received_data, DATA)

    async def test_rest_trigger(self):
        finish = asyncio.Event()

        async with PubSubClient() as client:
            async def on_event(data, topic):
                self.assertEqual(data, DATA)
                finish.set()

            client.subscribe(EVENT_TOPIC, on_event)  # type: ignore
            client.start_client(ws_url)
            await client.wait_until_ready()

            # trigger publish via rest call
            response = httpx.get(trigger_url)
            self.assertEqual(200, response.status_code)

            # wait for finish trigger
            await asyncio.wait_for(finish.wait(), 5)

@unittest.skip("TODO fix on CI build")
class TestRpc(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        next(server())

    async def test_invoke_server(self):
        async with PubSubClient() as ps_client:
            ps_client.start_client(ws_url)
            self.assertIsNone(ps_client._rpc_channel)
            await ps_client.wait_until_ready()
            assert isinstance(ps_client._rpc_channel, RpcChannel), "Actual type: " + type(ps_client._rpc_channel).__name__
            result: RpcResponse[str] = await ps_client._rpc_channel.other.to_upper(x="bar")
            self.assertEqual("BAR", result.result)

    async def test_invoke_client(self):
        async with PubSubClient() as ps_client:
            ps_client.start_client(ws_url)
            self.assertIsNone(ps_client._rpc_channel)
            await ps_client.wait_until_ready()
            assert isinstance(ps_client._rpc_channel, RpcChannel), "Actual type: " + type(ps_client._rpc_channel).__name__
            channel_id = ps_client._rpc_channel.id
            self.assertIsNotNone(channel_id)


if __name__ == "__main__":
    unittest.main()
