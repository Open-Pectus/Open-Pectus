from argparse import ArgumentParser
import os
from fastapi import FastAPI
from fastapi.routing import APIRoute
import uvicorn

from openpectus.aggregator.spa import SinglePageApplication
from openpectus.aggregator.routers import batch_job, process_unit, aggregator_websocket
from openpectus.aggregator.frontend_ws import poc


# - add lsp thingys
# - start (manage) lsp server instance for each client
# - aggregator-engine protocol


# Start env in docker
# ../docker compose up --build

# start local
# python -m uvicorn main:app --reload --port 8300

# check generation openapi.json() from build action, see https://github.com/tiangolo/fastapi/issues/2877
# possibly https://pypi.org/project/fastapi-openapi-generator/

# hints for
# https://stackoverflow.com/questions/67849806/flask-how-to-automate-openapi-v3-documentation

# Look into this https://stackoverflow.com/questions/74137116/how-to-hide-a-pydantic-discriminator-field-from-fastapi-docs
# Final / Literal ...

default_frontend_dist_dir = os.path.join(os.path.dirname(__file__), "frontend-dist")


def get_args():
    parser = ArgumentParser("Start Aggregator server")
    parser.add_argument("-host", "--host", required=False, default="127.0.0.1",
                        help="Host address to bind web socket to")
    parser.add_argument("-p", "--port", required=False, type=int, default="9800",
                        help="Port to bind web socket to")
    parser.add_argument("-fdd", "--frontend_dist_dir", required=False, default=default_frontend_dist_dir,
                        help="Frontend distribution directory. Defaults to " + default_frontend_dist_dir)
    return parser.parse_args()


def create_app(frontend_dist_dir: str = default_frontend_dist_dir):
    if not os.path.exists(frontend_dist_dir):
        raise FileNotFoundError("frontend_dist_dir not found: " + frontend_dist_dir)

    def custom_generate_unique_id(route: APIRoute):
        return f"{route.name}"

    title = "Pectus Aggregator"
    print(f"*** {title} ***")

    app = FastAPI(title=title, generate_unique_id_function=custom_generate_unique_id)

    prefix = "/api"
    app.include_router(process_unit.router, prefix=prefix)
    app.include_router(batch_job.router, prefix=prefix)
    app.include_router(aggregator_websocket.router)
    app.include_router(poc.router, prefix=prefix)

    app.mount("/", SinglePageApplication(directory=frontend_dist_dir))

    return app


def main():
    args = get_args()
    app = create_app(args.frontend_dist_dir)
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
