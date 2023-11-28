import os
from typing import List

import uvicorn
from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.deps import _create_aggregator
from openpectus.aggregator.aggregator import Aggregator
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from openpectus.aggregator.frontend_ws import frontend_pubsub
from openpectus.aggregator.routers import process_unit, batch_job, auth
from openpectus.aggregator.spa import SinglePageApplication
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher



class AggregatorServer:
    default_title = "Pectus Aggregator"
    default_frontend_dist_dir = os.path.join(os.path.dirname(__file__), "frontend-dist")
    default_host = "127.0.0.1"
    default_port = 9800

    def __init__(self, title: str = default_title, host: str = default_host, port: int = default_port, frontend_dist_dir: str = default_frontend_dist_dir):
        self.title = title
        self.host = host
        self.port = port
        self.frontend_dist_dir = frontend_dist_dir
        dispatcher = AggregatorDispatcher()
        aggregator = _create_aggregator(dispatcher)
        AggregatorMessageHandlers(aggregator)
        self.setup_fastapi([dispatcher.router])

    def setup_fastapi(self, additional_routers: List[APIRouter] = []):
        api_prefix = "/api"

        def custom_generate_unique_id(route: APIRoute):
            return f"{route.name}"
        self.fastapi = FastAPI(title=self.title, generate_unique_id_function=custom_generate_unique_id)
        self.fastapi.include_router(process_unit.router, prefix=api_prefix)
        self.fastapi.include_router(batch_job.router, prefix=api_prefix)
        self.fastapi.include_router(frontend_pubsub.router, prefix=api_prefix)
        self.fastapi.include_router(auth.router, prefix='/auth')
        for route in additional_routers : self.fastapi.include_router(route)
        if not os.path.exists(self.frontend_dist_dir):
            raise FileNotFoundError("frontend_dist_dir not found: " + self.frontend_dist_dir)
        self.fastapi.mount("/", SinglePageApplication(directory=self.frontend_dist_dir))



    def start(self):
        print(f"Serving frontend at http://{self.host}:{self.port}")
        uvicorn.run(self.fastapi, host=self.host, port=self.port)
