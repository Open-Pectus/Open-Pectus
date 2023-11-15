from fastapi import APIRouter, Depends

import openpectus.aggregator.deps as agg_deps
from openpectus.aggregator.protocol import Aggregator


router = APIRouter(tags=["aggregator"])

# (1) So, this works
# make sure the singleton aggregator is created before web server starts
agg_deps.create_aggregator(router)

# (2) But this does not. It causes the engine websocket connection to fail with a 500 Internal server error. weird.
# The server error turns up as an assertion failure:
# assert scope["type"] == "http"
# probably because of https://github.com/tiangolo/fastapi/discussions/6114 https://fastapi.tiangolo.com/tutorial/path-params/?h=order+matters#order-matters
# @router.on_event("startup")
# async def startup():
#     # make sure the singleton aggregator is created during web server startup
#     _ = agg_deps.create_aggregator(router)


@router.get("/health")
def health(aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
    if aggregator is None:
        raise Exception("Not healthy")

    return "healthy"
