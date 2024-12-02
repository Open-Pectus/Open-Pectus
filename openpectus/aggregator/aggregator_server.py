import logging
import os

import uvicorn
from openpectus.aggregator.routers.auth import UserRolesDependency
from alembic.config import Config
from fastapi import FastAPI, APIRouter
from fastapi.routing import APIRoute
from openpectus.aggregator.aggregator_message_handlers import AggregatorMessageHandlers
from openpectus.aggregator.data import database
from openpectus.aggregator.deps import _create_aggregator
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.routers import process_unit, recent_runs, auth, version
from openpectus.aggregator.spa import SinglePageApplication
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher


class AggregatorServer:
    default_title = "Pectus Aggregator"
    default_frontend_dist_dir = os.path.join(os.path.dirname(__file__), "frontend-dist")
    # default_frontend_dist_dir = ".\\openpectus\\frontend\\dist"
    default_host = "127.0.0.1"
    default_port = 9800

    def __init__(self, title: str = default_title, host: str = default_host, port: int = default_port,
                 frontend_dist_dir: str = default_frontend_dist_dir):
        self.title = title
        self.host = host
        self.port = port
        self.frontend_dist_dir = frontend_dist_dir
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
                               generate_unique_id_function=custom_generate_unique_id,
                               on_shutdown=[self.on_shutdown])
        self.fastapi.include_router(process_unit.router, prefix=api_prefix, dependencies=[UserRolesDependency])
        self.fastapi.include_router(recent_runs.router, prefix=api_prefix, dependencies=[UserRolesDependency])
        self.fastapi.include_router(auth.router, prefix='/auth')
        for route in additional_routers:
            self.fastapi.include_router(route)
        if not os.path.exists(self.frontend_dist_dir):
            raise FileNotFoundError("frontend_dist_dir not found: " + self.frontend_dist_dir)
        self.fastapi.mount("/", SinglePageApplication(directory=self.frontend_dist_dir))

    def init_db(self):
        alembic_ini_file_path = os.path.join(os.path.dirname(__file__), "alembic.ini")
        sqlalchemy_url = Config(alembic_ini_file_path).get_main_option('sqlalchemy.url')
        if sqlalchemy_url is None:
            raise ValueError('sqlalchemy.url not set in alembic.ini file')
        database.configure_db(sqlalchemy_url)
        self.fastapi.add_middleware(database.DBSessionMiddleware)

    def start(self):
        print(f"Serving frontend at http://{self.host}:{self.port}")
        uvicorn.run(self.fastapi, host=self.host, port=self.port, log_level=logging.WARNING)

    async def on_shutdown(self):
        await self.dispatcher.shutdown()
