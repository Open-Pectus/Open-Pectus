from typing import Awaitable, Callable, Any, TypeVar

import openpectus.protocol.aggregator_messages as AM
import openpectus.protocol.engine_messages as EM
import openpectus.protocol.messages as M

# --------- Dispatch interfaces ------------

AGGREGATOR_RPC_WS_PATH = "/engine-rpc"
AGGREGATOR_REST_PATH = "/engine-rest"
AGGREGATOR_HEALTH_PATH = "/health"
AGGREGATOR_AUTH_CONFIG_PATH = "/auth/config"
MessageHandler = Callable[[Any], Awaitable[M.MessageBase]]

AnyMessageType = TypeVar("AnyMessageType", bound=M.MessageBase)
EngineMessageType = TypeVar("EngineMessageType", bound=EM.EngineMessage)
AggregatorMessageType = TypeVar("AggregatorMessageType", bound=AM.AggregatorMessage)
