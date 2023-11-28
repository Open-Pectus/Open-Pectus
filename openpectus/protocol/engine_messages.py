from typing import List

import openpectus.protocol.messages as Msg
import openpectus.protocol.models as Mdl


class EngineMessage(Msg.MessageBase):
    engine_id: str | None = None


class RegisterEngineMsg(Msg.MessageBase):
    """ Doesn't extend EngineMessage, because we don't have the engine_id yet """
    computer_name: str
    uod_name: str
    # uod file hash, file change date


class UodInfoMsg(EngineMessage):
    readings: List[Mdl.ReadingInfo]


class TagsUpdatedMsg(EngineMessage):
    tags: List[Mdl.TagValue] = []


class RunLogMsg(EngineMessage):
    id: str
    runlog: Mdl.RunLog


class MethodMsg(EngineMessage):
    method: Mdl.Method


class ControlStateMsg(EngineMessage):
    control_state: Mdl.ControlState
