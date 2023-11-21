import logging
from typing import Awaitable, Callable

from openpectus.protocol.messages import MessageBase

# --------- Dispatch interfaces ------------

AGGREGATOR_RPC_WS_PATH = "/engine-rpc"
AGGREGATOR_REST_PATH = "/engine-rest"
AGGREGATOR_HEALTH_PATH = "/health"
MessageHandler = Callable[[MessageBase], Awaitable[MessageBase]]

logger = logging.getLogger(__name__)

