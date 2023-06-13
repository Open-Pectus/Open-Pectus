from fastapi import Depends
from protocol.aggregator import Aggregator, create_aggregator
from fastapi_websocket_pubsub import PubSubEndpoint

_server: Aggregator | None = None


def get_aggregator() -> Aggregator:
    global _server
    if _server is None:
        _server = create_aggregator()

    assert _server is not None
    return _server


def get_endpoint(server=Depends(get_aggregator)) -> PubSubEndpoint:
    assert server.endpoint is not None
    return server.endpoint
