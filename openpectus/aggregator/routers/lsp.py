import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import APIRouter, FastAPI
from fastapi_proxy_lib.core.websocket import ReverseWebSocketProxy
from httpx import AsyncClient
from starlette.websockets import WebSocket

logger = logging.getLogger(__name__)
router = APIRouter(tags=["lsp"], include_in_schema=False)
proxy = ReverseWebSocketProxy(AsyncClient(), base_url="ws://127.0.0.1:2087/")

@asynccontextmanager
async def close_proxy_event(_: FastAPI) -> AsyncIterator[None]:
    """Close proxy."""
    yield
    await proxy.aclose()

router.lifespan_context(close_proxy_event)

@router.websocket("/lsp")
async def _(websocket: WebSocket):
    return await proxy.proxy(websocket=websocket)
