from argparse import ArgumentParser
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.routing import APIRoute
import uvicorn

from openpectus.aggregator.spa import SinglePageApplication
from openpectus.aggregator.routers import batch_job, process_unit, aggregator_websocket

# - add lsp thingys
# - start (manage) lsp server instance for each client
# - aggregator-engine protocol

# Start env in docker
# ../docker compose up --build

# start local
# python -m uvicorn main:app --reload --port 8300
# or
# pectus-aggregator -r

# check generation openapi.json() from build action, see https://github.com/tiangolo/fastapi/issues/2877
# possibly https://pypi.org/project/fastapi-openapi-generator/

# hints for
# https://stackoverflow.com/questions/67849806/flask-how-to-automate-openapi-v3-documentation

# Look into this https://stackoverflow.com/questions/74137116/how-to-hide-a-pydantic-discriminator-field-from-fastapi-docs
# Final / Literal ...

default_frontend_dist_dirs = [
Path(__file__).parent/'frontend-dist',
Path(__file__).parent.parent/'frontend'/'dist',
]

def get_args():
    parser = ArgumentParser("Start Aggregator server")
    parser.add_argument("-host", "--host", required=False, default="127.0.0.1",
                        help="Host address to bind web socket to")
    parser.add_argument("-p", "--port", required=False, type=int, default="9800",
                        help="Port to bind web socket to")
    parser.add_argument("-fdd", "--frontend_dist_dir", required=False, default='',
                        help="Frontend distribution directory. Defaults to look at " + str(default_frontend_dist_dirs))
    parser.add_argument("-r", "--reload", required=False, default=False, action='store_true',
                        help="Reload Uvicorn automatically for local development.")
    return parser.parse_args()

def create_app(frontend_dist_dir: str = ''):
    if frontend_dist_dir != '' and not os.path.exists(frontend_dist_dir):
        raise FileNotFoundError("specified frontend_dist_dir not found: " + frontend_dist_dir)
    for frontend_dist_dir in default_frontend_dist_dirs:
        if os.path.exists(frontend_dist_dir):
            break
    else:
        raise FileNotFoundError("frontend_dist_dir not found among: " + str(default_frontend_dist_dirs))

    def custom_generate_unique_id(route: APIRoute):
        return f"{route.name}"

    title = "Pectus Aggregator"
    print(f"*** {title} ***")

    app = FastAPI(title=title, generate_unique_id_function=custom_generate_unique_id)

    prefix = "/api"
    app.include_router(process_unit.router, prefix=prefix)
    app.include_router(batch_job.router, prefix=prefix)
    app.include_router(aggregator_websocket.router)

    app.mount("/", SinglePageApplication(directory=frontend_dist_dir))

    return app

def app_factory():
    args = get_args()
    app = create_app(args.frontend_dist_dir)
    return app

def main():
    args = get_args()
    uvicorn.run('openpectus.aggregator.main:app_factory', host=args.host, port=args.port, reload=args.reload, factory=True)

if __name__ == "__main__":
    main()
