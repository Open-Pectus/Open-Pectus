from typing import List

import openpectus.protocol.messages as M


class AggregatorMessage(M.MessageBase):
    pass


class RegisterEngineReplyMsg(AggregatorMessage):
    success: bool
    engine_id: str | None


class UnregisteredEngineErrorMsg(M.ErrorMessage):
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


class MethodLineMsg(AggregatorMessage):
    id: str
    content: str


class MethodMsg(AggregatorMessage):
    lines: List[MethodLineMsg]
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]
