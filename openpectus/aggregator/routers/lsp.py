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

    patterns = [
        dict(name="comment.control.pcode", begin="#", end="$"), # P-code comments. Color: green
        dict(name="support.type.property-name", match=r"^\s*\d+(\.\d+)?\s"), # P-code thresholds. Color: bright red
    ]
    """
    A string such as "Block Time" can be interpreted either as the tag "Block Time"
    or as the system command "Block" and then the word "Time".
    The Monaco editor uses the first pattern that matches.

    Thus, patterns must be created such that the longest matches come first.
    This ensures that "Block Time" matches first.
    """
    style_associations = {
        "entity.name.class": tags, # Color: blue/green
        "constant.language.pcode": sys_cmds, # Color: blue
        "support.constant.color": uod_cmds, # Color: lighter blue
    }

    style_associations_per_item = []
    for style, items in style_associations.items():
        for item in items:
            style_associations_per_item.append((style, item))
    # Sort so items with most spaces come first.
    style_associations_per_item.sort(key=lambda x: x[1].count(" "), reverse=True)
    # Group style associations by number of spaces
    for n_spaces, group in groupby(style_associations_per_item, key=lambda x: x[1].count(" ")):
        # Group items by style
        for style, items in groupby(list(group), key=lambda x: x[0]):
            patterns.append(dict(
                name=style,
                match=fr"\b({'|'.join(item_name for item_style, item_name in items)})\b"
            ))

    return {
        "name": "PCode",
        "scopeName": "source.pcode",
        "fileTypes": "pcode",
        "patterns": patterns,
    }
