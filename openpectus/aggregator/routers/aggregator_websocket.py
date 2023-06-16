import sys
import os
from fastapi import APIRouter, Depends

op_path = os.path.join(os.path.dirname(__file__), "..", "..")
sys.path.append(op_path)

from protocol.aggregator import Aggregator
import aggregator.deps as agg_deps


router = APIRouter(tags=["aggregator"])


# make sure aggregator is created before web server starts
agg_deps.create_aggregator(router)


@router.get("/health")
def health(aggregator: Aggregator = Depends(agg_deps.get_aggregator)):
    if aggregator is None:
        raise Exception("Not healthy")

    return "healthy"
