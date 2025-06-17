from openpectus.aggregator.aggregator import Aggregator
from openpectus.aggregator.frontend_publisher import FrontendPublisher
from openpectus.aggregator.webpush_publisher import WebPushPublisher
from openpectus.protocol.aggregator_dispatcher import AggregatorDispatcher

_server: Aggregator | None = None


def get_aggregator() -> Aggregator:
    if _server is None:
        raise Exception("DI configuration error. Aggregator has not been initialized")
    return _server


def _create_aggregator(dispatcher: AggregatorDispatcher, publisher: FrontendPublisher, webpush_publisher: WebPushPublisher, secret: str) -> Aggregator:
    global _server
    if _server is not None:
        return _server
    else:
        _server = Aggregator(dispatcher, publisher, webpush_publisher, secret)
        # print("GLOBAL: Creating aggregator server")
        return _server
