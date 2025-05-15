import logging
import asyncio
from itertools import groupby

import openpectus.aggregator.deps as agg_deps
import openpectus.aggregator.models as Mdl
from openpectus.lsp.pylsp_plugin import OPPythonLSPServer
from fastapi import APIRouter, Depends, HTTPException, WebSocket
from openpectus.aggregator.aggregator import Aggregator
from starlette.status import HTTP_404_NOT_FOUND

logger = logging.getLogger(__name__)
router = APIRouter(tags=["lsp"], prefix="/lsp", include_in_schema=True)


def get_registered_engine_data_or_fail(engine_id: str, agg: Aggregator) -> Mdl.EngineData:
    engine_data = agg.get_registered_engine_data(engine_id)
    if engine_data is None:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)
    return engine_data

@router.get("/pcode.language-configuration.json")
def get_pcode_language_configuration():
    return {
        "comments": {"lineComment": "#"},
        "onEnterRules": [
            {
                "beforeText": {"pattern": '^\\s*(Alarm|Block|Watch|Macro).*$'},
                "action": {"indent": 'indent'},
            },
            {
                "beforeText": {"pattern": '^\\s*End block$'},
                "action": {"indent": 'outdent'},
            },
            {
                "beforeText": {"pattern": r'^\s*(\n|\r)*$'},
                "action": {"indent": 'outdent'},
            },
            {
                "beforeText": {"pattern": '^\\s*End blocks$'},
                "action": {"indent": 'none', "removeText": 1000},
            }
        ]
    }

@router.get('/engine/{engine_id}/pcode.tmLanguage.json', response_model_exclude_none=True)
def get_pcode_tm_grammar(engine_id: str, agg: Aggregator = Depends(agg_deps.get_aggregator)):
    engine_data = get_registered_engine_data_or_fail(engine_id, agg)
    if engine_data.uod_definition is None:
        logger.error(f"engine_data.uod_definition is none, {engine_id=}")
        raise HTTPException(status_code=HTTP_404_NOT_FOUND)

    sys_cmds = [c.name for c in engine_data.uod_definition.system_commands]
    uod_cmds = [c.name for c in engine_data.uod_definition.commands]
    tags = [t.name for t in engine_data.uod_definition.tags]

    patterns = [
        dict(name="comment.control.pcode", begin="#", end="$"),  # P-code comments. Color: green
        dict(name="support.type.property-name", match=r"^\s*\d+(\.\d+)?\s"),  # P-code thresholds. Color: bright red
    ]
    """
    A string such as "Block Time" can be interpreted either as the tag "Block Time"
    or as the system command "Block" and then the word "Time".
    The Monaco editor uses the first pattern that matches.

    Thus, patterns must be created such that the longest matches come first.
    This ensures that "Block Time" matches first.
    """

    styles = {
        "tag": "entity.name.class",  # Color: blue/green
        "sys_cmd": "constant.language.pcode",  # Color: blue
        "uod_cmd": "support.constant.color",  # Color: lighter blue
    }

    color_types = {
        "tag": tags,
        "sys_cmd": sys_cmds,
        "uod_cmd": uod_cmds,
    }

    color_type_item = [(color_type, item) for color_type, items in color_types.items() for item in items]
    # Sort so items with most spaces come first.
    color_type_item.sort(key=lambda x: x[1].count(" "), reverse=True)
    # Group color_type associations by number of spaces
    for n_spaces, group in groupby(color_type_item, key=lambda x: x[1].count(" ")):
        # Group items by color_type
        for color_type, items in groupby(list(group), key=lambda x: x[0]):
            # For tag names to match, they must be preceeded by a colon.
            # This is required because it is otherwise ambiguous if e.g.
            # "Block" should match the Block command or the Block tag.
            prefix = "(?<=:[^:]*)" if color_type == "tag" else ""
            pattern = dict(
                name=styles[color_type],
                match=prefix + fr"\b({'|'.join(item_name for item_color_type, item_name in items)})\b"
            )
            patterns.append(pattern)

    return {
        "name": "PCode",
        "scopeName": "source.pcode",
        "fileTypes": "pcode",
        "patterns": patterns,
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

    lsp_handler = OPPythonLSPServer(
        rx=None,
        tx=None,
        consumer=send_message,
    )

    async for message in websocket.iter_json():
        lsp_handler.consume(message)
        # If the message is "exit" then we can close the websocket
        # It would be cleaner to get some sort of signal that the LSP handler
        # got this exit message. Unfortunately there is no API to accomplish this.
        if message.get("method", None) == "exit":
            await websocket.close()
            break
