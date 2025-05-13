import logging
import asyncio

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
import openpectus.aggregator.routers.dto as Dto
from fastapi import APIRouter, Depends, Response, HTTPException, WebSocket
from openpectus.aggregator.aggregator import Aggregator
from starlette.status import HTTP_404_NOT_FOUND
from pylsp.python_lsp import PythonLSPServer


logger = logging.getLogger(__name__)
router = APIRouter(tags=["lsp"], prefix="/lsp", include_in_schema=True)


def get_registered_engine_data_or_fail(engine_id: str, agg: Aggregator) -> Mdl.EngineData:
    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return engine_data


@router.get('/engine/{engine_id}/pcode.tmLanguage.json', response_model_exclude_none=True)
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
                "name": "constant.language.pcode",  # color: blue, content: system commands
                "match": f"\\b({'|'.join(sys_cmds)})\\b",
            },
            {
                "name": "support.constant.color",  # color: lighter blue, content: uod commands
                "match": f"\\b({'|'.join(uod_cmds)})\\b",
            },
            {
                "name": "comment.control.pcode",  # color: green, content: comments
                "begin": "#",
                "end": "$"
            },
            {
                "name": "support.type.property-name",  # color: bright red, content: thresholds
                "match": "^\\s*\\d+(\\.\\d+)?\\s",
            },            {
                "name": "entity.name.class",  # color: blue/green, content: tags
                "match": f"\\b({'|'.join(tags)})\\b",
            },
        ]
    }


@router.websocket("/websocket")
async def lsp_server_endpoint(websocket: WebSocket):
    await websocket.accept()
    loop = asyncio.get_event_loop()
    tasks = set()

    def send_message(message):
        task = loop.create_task(websocket.send_json(message))
        tasks.add(task)
        task.add_done_callback(tasks.discard)

    lsp_handler = PythonLSPServer(
        rx=None,
        tx=None,
        consumer=send_message,
    )

    async for message in websocket.iter_json():
        lsp_handler.consume(message)
