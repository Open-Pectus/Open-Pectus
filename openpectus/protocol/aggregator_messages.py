from typing import List

import openpectus.protocol.messages as Msg
import openpectus.protocol.models as Mdl


class AggregatorMessage(Msg.MessageBase):
    pass


class RegisterEngineReplyMsg(AggregatorMessage):
    success: bool
    engine_id: str | None = None


class UnregisteredEngineErrorMsg(Msg.ErrorMessage):
    pass


class InvokeCommandMsg(AggregatorMessage):
    name: str = ""
    arguments: str | None = None


class InjectCodeMsg(AggregatorMessage):
    pcode: str


class TagSpec(AggregatorMessage):
    tag_name: str
    tag_unit: str | None


# class UodSpecMsg(AggregatorMessage):
#     name: str
#     tags: List[TagSpec] = []


class MethodMsg(AggregatorMessage):
    method: Mdl.Method
