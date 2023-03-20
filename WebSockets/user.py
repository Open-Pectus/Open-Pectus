'''
Users can connect to the Aggregator and
subscribe to data from a specific engine.
'''

# Adapted from this source:
#https://github.com/permitio/fastapi_websocket_pubsub/blob/master/examples/pubsub_client_example.py

import asyncio
from fastapi_websocket_pubsub import PubSubClient

PORT = 8000

async def main():
    client = PubSubClient([])

    async def send_action_to_engine(engine):
        response = await client._rpc_channel.other.call_engine(engine=engine, fn='action', a=5, b=4)
        if response is False:
            print(f'It seems that engine {engine} does not exist.')

    async def on_data(topic, data):
        engine = data['engine']
        live_data = data['data']['live_data']
        print(f'<< {engine:04d} {live_data:04d}')
        asyncio.create_task(send_action_to_engine(int(engine)))

    client.subscribe('U', on_data)
    client.start_client(f"ws://localhost:{PORT}/pubsub")
    await client.wait_until_ready()
    await client.wait_until_done()

asyncio.run(main())