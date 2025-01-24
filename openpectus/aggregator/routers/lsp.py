import logging

from openpectus.aggregator import command_util
import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, Depends, Response, HTTPException
from openpectus.aggregator.aggregator import Aggregator
from starlette.status import HTTP_404_NOT_FOUND


logger = logging.getLogger(__name__)
router = APIRouter(tags=["lsp"], include_in_schema=False)


def get_registered_engine_data_or_fail(engine_id: str, agg: Aggregator) -> Mdl.EngineData:
    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return engine_data


# changes to do
# - maybe rename to something more generic
# - return uod command validation as "command argument spec data" so lsp server can validate using this data rather than a local uod
# - include "command argument spec data" for internal engine commands
@router.get('/uod/{engine_id}', response_model_exclude_none=True)
def get_uod_info(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)
        ) -> Dto.UodDefinition:
    response.headers["Cache-Control"] = "no-store"
    engine_data = get_registered_engine_data_or_fail(engine_id, agg)
    return Dto.UodDefinition(
        name=engine_data.uod_name, filename=engine_data.uod_filename
    )
