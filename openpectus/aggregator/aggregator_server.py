import os
from typing import List

import uvicorn
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.aggregator.data.repository import PlotLogRepository
from openpectus.aggregator.deps import _create_aggregator
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.routers import process_unit, batch_job, auth
from openpectus.aggregator.spa import SinglePageApplication
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher


class AggregatorServer:
    default_title = "Pectus Aggregator"
    default_frontend_dist_dir = os.path.join(os.path.dirname(__file__), "frontend-dist")
    default_database_file_path = "./aggregator_data.db"
    default_host = "127.0.0.1"
    default_port = 9800

    def __init__(self, title: str = default_title, host: str = default_host, port: int = default_port,
                 frontend_dist_dir: str = default_frontend_dist_dir, database_file_path: str = default_database_file_path):
        self.title = title
        self.host = host
        self.port = port
        self.frontend_dist_dir = frontend_dist_dir
        self.database_file_path = database_file_path
        dispatcher = AggregatorDispatcher()
        publisher = FrontendPublisher()
        aggregator = _create_aggregator(dispatcher, publisher)
        _ = AggregatorMessageHandlers(aggregator)
        self.setup_fastapi([dispatcher.router, publisher.router])
        self.init_db()

    def setup_fastapi(self, additional_routers: List[APIRouter] = []):
        api_prefix = "/api"

        def custom_generate_unique_id(route: APIRoute):
            return f"{route.name}"

        self.fastapi = FastAPI(title=self.title, generate_unique_id_function=custom_generate_unique_id)
        self.fastapi.include_router(process_unit.router, prefix=api_prefix)
        self.fastapi.include_router(batch_job.router, prefix=api_prefix)
        self.fastapi.include_router(auth.router, prefix='/auth')
        for route in additional_routers:
            self.fastapi.include_router(route)
        if not os.path.exists(self.frontend_dist_dir):
            raise FileNotFoundError("frontend_dist_dir not found: " + self.frontend_dist_dir)
        self.fastapi.mount("/", SinglePageApplication(directory=self.frontend_dist_dir))

    def init_db(self):
        database.configure_db(self.database_file_path)
        database.create_db()

    def start(self):
        print(f"Serving frontend at http://{self.host}:{self.port}")
        uvicorn.run(self.fastapi, host=self.host, port=self.port)
