import openpectus.protocol.messages as Msg
import openpectus.protocol.models as Mdl

# Note: These are the messages sent by AggregatorDispatcher and handled by EngineMessageHandlers.


SuccessMessage = Msg.SuccessMessage
ErrorMessage = Msg.ErrorMessage


class AggregatorMessage(Msg.MessageBase):
    """ Marker class that indicates a protocol message sent by Aggregator to Engine.

    On the Engine side, they are handled by EngineMessageHandlers.
    """
    pass


class RegisterEngineReplyMsg(AggregatorMessage):
    """ Reply to a RegisterEngineMsg from engine. """
    success: bool
    engine_id: str | None = None
    secret_match: bool

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_id="{self.engine_id}", success={self.success})'


class InvokeCommandMsg(AggregatorMessage):
    """ Request from user to invoke a command. """
    name: str = ""
    arguments: str | None = None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}", arguments={self.arguments})'


class InjectCodeMsg(AggregatorMessage):
    """ Request from user to inject pcode. """
    pcode: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(pcode="{self.pcode}")'


class MethodMsg(AggregatorMessage):
    """ Request from user to set a new method to be executed by engine. """
    method: Mdl.Method

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(method="{self.method}")'


class CancelMsg(AggregatorMessage):
    """ Request from user to cancel an instruction. """
    exec_id: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(exec_id="{self.exec_id}")'


class ForceMsg(AggregatorMessage):
    """ Request from user to force an instruction to start. """
    exec_id: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(exec_id="{self.exec_id}")'
