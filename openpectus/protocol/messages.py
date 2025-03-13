from pydantic import BaseModel

# Topics

# No topics in aggregator-engine protocol, rest and rpc only


# Messages

class MessageBase(BaseModel):
    """ Base class for protocol messages for both REST and WebSocket communication.

    These inherit from pydantic BaseModel to support automatic (de-)serialization when sent over
    fastapi_websocket_pubsub. Additionally they support automatic openapi schema generation for
    use with REST.

    Unfortunately, for websocket rpc, (de-)serialization is not automatic but is handled using
    the openpectus.protocol.serialization module.
    """
    version: int = 0
    """ Protocol is currently unversioned. This field is included to support future versioning. """

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(version="{self.version}")'


class SuccessMessage(MessageBase):
    """ Indicates operation success"""
    pass


class ErrorMessage(MessageBase):
    """ Returned whenever an error occurs"""
    message: str | None = None
    exception_message: str | None = None
    caller_error: bool = False

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(version="{self.version}", message="{self.message}", ' +
                f'exception_message="{self.exception_message}")')


class ProtocolErrorMessage(ErrorMessage):
    protocol_msg: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(version="{self.version}", protocol_msg="{self.protocol_msg}")'


RpcErrorMessage = ErrorMessage | ProtocolErrorMessage
RpcStatusMessage = SuccessMessage | RpcErrorMessage


# RpcValueMessage = MessageBase | RpcErrorMessage
