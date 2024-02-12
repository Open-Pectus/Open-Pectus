from typing import List

import openpectus.protocol.messages as Msg
import openpectus.protocol.models as Mdl

# Note: These are the messages sent by EngineDispatcher and handled by AggregatorMessageHandlers.


class EngineMessage(Msg.MessageBase):
    engine_id: str = ''


class RegisterEngineMsg(Msg.MessageBase):
    """ Doesn't extend EngineMessage, because we don't have the engine_id yet """
    computer_name: str
    uod_name: str
    location: str
    engine_version: str
    # uod file hash, file change date


class UodInfoMsg(EngineMessage):
    readings: List[Mdl.ReadingInfo]
    plot_configuration: Mdl.PlotConfiguration
    hardware_str: str


class TagsUpdatedMsg(EngineMessage):
    tags: List[Mdl.TagValue] = []


class RunLogMsg(EngineMessage):
    id: str
    runlog: Mdl.RunLog

class ErrorLogMsg(EngineMessage):
    log: Mdl.ErrorLog

class MethodMsg(EngineMessage):
    method: Mdl.Method


class MethodStateMsg(EngineMessage):
    method_state: Mdl.MethodState


class ControlStateMsg(EngineMessage):
    control_state: Mdl.ControlState
