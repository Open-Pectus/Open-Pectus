import logging
from typing import Awaitable, Callable

from openpectus.protocol.messages import MessageBase

# --------- Dispatch interfaces ------------

AGGREGATOR_RPC_WS_PATH = "/AE_rpc"
AGGREGATOR_POST_PATH = "/AE_post"
MessageHandler = Callable[[MessageBase], Awaitable[MessageBase]]

logger = logging.getLogger(__name__)

