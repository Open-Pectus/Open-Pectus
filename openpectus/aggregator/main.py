from fastapi import FastAPI
from fastapi.routing import APIRoute

from routers import batch_job, process_unit
from spa import SinglePageApplication


# TODO
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


def custom_generate_unique_id(route: APIRoute):
    return f"{route.name}"


title = "Pectus Aggregator"
prefix = "/api"
print(f"*** {title} ***")
app = FastAPI(title=title, generate_unique_id_function=custom_generate_unique_id)
app.include_router(process_unit.router, prefix=prefix)
app.include_router(batch_job.router, prefix=prefix)
app.mount("/", SinglePageApplication(directory='frontend-dist'))
