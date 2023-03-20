'''
The Aggregator allows engines to register
themselves and accept the data they push.
Users can also connect and subscribe to
data from specific engines and send commands
back to the engines.
'''

# Adapted from this source
# https://github.com/permitio/fastapi_websocket_pubsub/blob/master/examples/pubsub_server_example.py

import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi_websocket_pubsub import PubSubEndpoint

app =  FastAPI()

rpc_channels = {}

# Methods to expose to the clients
from fastapi_websocket_pubsub.rpc_event_methods import RpcEventServerMethods
class AggregatorServer(RpcEventServerMethods):
    async def call_engine(self, engine, fn, *args, **kwargs):
        '''
        This endpoint forwards function calls from a User
        to a specific Engine.
        '''
        global rpc_channels
        print(rpc_channels)
        
        if engine in rpc_channels:
            ch = rpc_channels[engine]
            async def f():
                await getattr(ch.other, fn)(*args, **kwargs)
            asyncio.create_task(f())
            return True
        return False
    async def register_engine(self, engine_id):
        '''
        This endpoint is called by Engines
        that want to register themselves.
        This is done by letting the Aggregator
        subscribe to data from the Engine and
        blindly pass it on to any Users.
        '''
        print(f'Registering engine {engine_id}')
        global rpc_channels
        rpc_channels[engine_id] = self.channel
        
        async def forward_data_to_users(topic, data):
            print('>>', topic, data)
            data = {'engine':engine_id, 'data': data}
            await psendpoint.publish(['U', f'U{engine_id:d}'], data=data)
        await psendpoint.subscribe([f'E{engine_id:d}'], forward_data_to_users)

#PubSub stuff
router = APIRouter()
psendpoint = PubSubEndpoint(methods_class=AggregatorServer)
psendpoint.register_route(router, '/pubsub')
app.include_router(router)

# Start the server itself
uvicorn.run(app, host='localhost', port=8000)