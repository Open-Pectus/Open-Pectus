import logging
import os

import uvicorn
from openpectus.aggregator.routers.auth import UserRolesDependency
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from openpectus import __version__
from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.aggregator.deps import _create_aggregator
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.routers import process_unit, recent_runs, auth, version
from openpectus.aggregator.spa import SinglePageApplication
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher


class AggregatorServer:
    default_title = "Open Pectus Aggregator"
    default_frontend_dist_dir = os.path.join(os.path.dirname(__file__), "frontend-dist")
    default_host = "127.0.0.1"
    default_port = 9800
    default_db_filename = "open_pectus_aggregator.sqlite3"
    default_db_path = os.path.join(os.getcwd(), default_db_filename)

    def __init__(self, title: str = default_title, host: str = default_host, port: int = default_port,
                 frontend_dist_dir: str = default_frontend_dist_dir, db_path: str = default_db_path):
        self.title = title
        self.host = host
        self.port = port
        self.frontend_dist_dir = frontend_dist_dir
        self.db_path = db_path
        if not os.path.exists(frontend_dist_dir):
            raise FileNotFoundError("{frontend_dist_dir} not found.")
        self.dispatcher = AggregatorDispatcher()
        self.publisher = FrontendPublisher()
        self.aggregator = _create_aggregator(self.dispatcher, self.publisher)
        _ = AggregatorMessageHandlers(self.aggregator)
        self.setup_fastapi([self.dispatcher.router, self.publisher.router, version.router])
        self.init_db()

    def setup_fastapi(self, additional_routers: list[APIRouter] = []):
        api_prefix = "/api"

        def custom_generate_unique_id(route: APIRoute):
            return f"{route.name}"

        self.fastapi = FastAPI(title=self.title,
                               version=__version__,
                               contact=dict(name="Open Pectus",
                                            url="https://github.com/Open-Pectus/Open-Pectus"),
                               generate_unique_id_function=custom_generate_unique_id,
                               on_shutdown=[self.on_shutdown])
        self.fastapi.include_router(process_unit.router, prefix=api_prefix, dependencies=[UserRolesDependency])
        self.fastapi.include_router(recent_runs.router, prefix=api_prefix, dependencies=[UserRolesDependency])
        self.fastapi.include_router(auth.router, prefix="/auth")
        for route in additional_routers:
            self.fastapi.include_router(route)
        self.fastapi.mount("/", SinglePageApplication(directory=self.frontend_dist_dir))

    def init_db(self):
        database.configure_db(f"sqlite:///{self.db_path}")
        self.fastapi.add_middleware(database.DBSessionMiddleware)

    def start(self):
        uvicorn.run(self.fastapi, host=self.host, port=self.port, log_level=logging.WARNING)

    async def on_shutdown(self):
        await self.dispatcher.shutdown()
