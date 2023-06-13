import os
import sys
from fastapi import FastAPI
from fastapi.routing import APIRoute
import uvicorn
from routers import batch_job, process_unit
from spa import SinglePageApplication

# TODO replace hack with pip install -e, eg https://stackoverflow.com/questions/30306099/pip-install-editable-vs-python-setup-py-develop
op_path = os.path.join(os.path.dirname(__file__), "..")
sys.path.append(op_path)


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
print(f"*** {title} ***")

app = FastAPI(title=title, generate_unique_id_function=custom_generate_unique_id)

prefix = "/api"
app.include_router(process_unit.router, prefix=prefix)
app.include_router(batch_job.router, prefix=prefix)

app.mount("/", SinglePageApplication(directory=os.path.join(os.path.dirname(__file__), "frontend-dist")))


if __name__ == "__main__":
    PORT = 9800    
    uvicorn.run(app, host="127.0.0.1", port=PORT)
