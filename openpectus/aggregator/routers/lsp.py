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


@router.get('/tags/{engine_id}', response_model_exclude_none=True)
def get_tags(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)
        ) -> list[Dto.TagDefinition]:
    response.headers["Cache-Control"] = "no-store"
    engine_data = get_registered_engine_data_or_fail(engine_id, agg)
    return [
        Dto.TagDefinition(name=t.name, unit=t.value_unit)
        for t in engine_data.tags_info.values()
    ]

@router.get('/commands/{engine_id}', response_model_exclude_none=True)
def get_commands(
        engine_id: str,
        response: Response,
        agg: Aggregator = Depends(agg_deps.get_aggregator)
        ) -> list[Dto.CommandDefinition]:
    response.headers["Cache-Control"] = "no-store"
    engine_data = get_registered_engine_data_or_fail(engine_id, agg)
    tags_info = engine_data.tags_info.map
    process_values: list[Dto.ProcessValue] = []
    for tag_value in tags_info.values():
        matching_reading = next((r for r in engine_data.readings if r.tag_name == tag_value.name), None)
        if matching_reading is not None:
            try:
                cmds = command_util.create_reading_commands(tag_value, matching_reading)
                process_values.append(Dto.ProcessValue.create_w_commands(tag_value, cmds))
            except Exception as ex:
                logger.error(f"Error creating commands for process value '{matching_reading.tag_name}': {ex}")
        else:
            process_values.append(Dto.ProcessValue.create(tag_value))

    cmd_defs: list[Dto.CommandDefinition] = []
    for p in process_values:
        if p.commands is not None:
            for p_cmd in p.commands:
                cmd_defs.append(Dto.CommandDefinition(name=p_cmd.name))
    return cmd_defs


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
