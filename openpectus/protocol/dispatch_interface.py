import logging
from typing import Awaitable, Callable, Any

from openpectus.protocol.messages import MessageBase

# --------- Dispatch interfaces ------------

AGGREGATOR_RPC_WS_PATH = "/engine-rpc"
AGGREGATOR_REST_PATH = "/engine-rest"
AGGREGATOR_HEALTH_PATH = "/health"
MessageHandler = Callable[[Any], Awaitable[MessageBase]]

logger = logging.getLogger(__name__)

