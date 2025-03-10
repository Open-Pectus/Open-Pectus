import logging

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


@router.get('/lsp/uod/{engine_id}', response_model_exclude_none=True)
def get_uod_info(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)
        ) -> Dto.UodDefinition:
    response.headers["Cache-Control"] = "no-store"
    engine_data = get_registered_engine_data_or_fail(engine_id, agg)
    uod_definition = engine_data.uod_definition
    if uod_definition is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return Dto.UodDefinition.from_model(uod_definition)


@router.get('/uod/{engine_id}/pcode.tmLanguage.json', response_model_exclude_none=True)
def get_pcode_tm_grammar(engine_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    engine_data = get_registered_engine_data_or_fail(engine_id, agg)
    if engine_data.uod_definition is None:
        logger.error(f"engine_data.uod_definition is none, {engine_id=}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    sys_cmds = [c.name for c in engine_data.uod_definition.system_commands]
    uod_cmds = [c.name for c in engine_data.uod_definition.commands]
    tags = [t.name for t in engine_data.uod_definition.tags]

    return {
        "name": "PCode",
        "scopeName": "source.pcode",
        "fileTypes": "pcode",
        "patterns": [
            {
                "name": "constant.language.pcode",  # color: blue
                "match": f"\\b({'|'.join(sys_cmds)})\\b",
            },
            {
                "name": "support.constant.color",  # color: lighter blue
                "match": f"\\b({'|'.join(uod_cmds)})\\b",
            },
            {
                "name": "comment.control.pcode",  # color: green
                "begin": "#",
                "end": "$"
            },
            {
                "name": "support.type.property-name",  # color: bright red
                "match": "^\\d+(\\.\\d+)?\\s",
            },            {
                "name": "entity.name.class",  # color: blue/green
                "match": f"\\b({'|'.join(tags)})\\b",
            },
        ]
    }
