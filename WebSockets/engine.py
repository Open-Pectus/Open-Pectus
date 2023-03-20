'''
The engine connects with the Aggregator
and registers itself.
After registration it will periodically
send data to the aggregator.
'''

# Adapted from this source:
#https://github.com/permitio/fastapi_websocket_pubsub/blob/master/examples/pubsub_client_example.py

import asyncio
import random
from fastapi_websocket_pubsub import PubSubClient
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventClientMethods

PORT = 8000
engine_id = int(random.random()*1000)

class EngineServer(RpcEventClientMethods):
    async def action(self, *args, **kwargs):
        print('Engine was served an action:', kwargs)

async def main():
    client = PubSubClient([], methods_class=EngineServer)
    
    client.start_client(f"ws://localhost:{PORT}/pubsub")
    await client.wait_until_ready()
    await client._rpc_channel.other.register_engine(engine_id=engine_id)
    while 1:
        await asyncio.sleep(1)
        #if client.is_ready() and client._rpc_channel is not None:
        #    await client._rpc_channel.other.register_engine(engine_id=2)
        live_data = int(random.random()*1000)
        await client.publish([f'E{engine_id:d}'], data={'live_data': live_data,})
        print(f'>> {engine_id:04d} {live_data:04d}')
    await client.wait_until_done()

asyncio.run(main())