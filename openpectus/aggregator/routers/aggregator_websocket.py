from fastapi import APIRouter, Depends

import openpectus.aggregator.deps as agg_deps
from openpectus.protocol.aggregator import Aggregator


router = APIRouter(tags=["aggregator"])


# make sure aggregator is created before web server starts
agg_deps.create_aggregator(router)


@router.get("/health")
def health(aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
    if aggregator is None:
        raise Exception("Not healthy")

    return "healthy"
