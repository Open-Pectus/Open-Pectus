from datetime import datetime
from typing import List

import openpectus.protocol.messages as Msg
import openpectus.protocol.models as Mdl


# Note: These are the messages sent by EngineDispatcher and handled by AggregatorMessageHandlers.


class EngineMessage(Msg.MessageBase):
    sequence_number: int = -1
    engine_id: str = ''

    @property
    def ident(self) -> str:
        return f"seq: {self.sequence_number: >3}, type: {type(self).__name__}"

class RegisterEngineMsg(Msg.MessageBase):
    """ Doesn't extend EngineMessage, because we don't have the engine_id yet """
    computer_name: str
    uod_name: str
    location: str
    engine_version: str
    # uod file hash, file change date

    sequence_number: int = -2

    @property
    def ident(self) -> str:
        return f"seq: {self.sequence_number: >3}, type: {type(self).__name__}"


class UodInfoMsg(EngineMessage):
    readings: List[Mdl.ReadingInfo]
    plot_configuration: Mdl.PlotConfiguration
    hardware_str: str


class ReconnectedMsg(EngineMessage):
    run_id: str | None
    run_started_tick: float | None
    tags: List[Mdl.TagValue] = []
    sequence_number = -3


# class SyncTagsMsg(EngineMessage):
#     tags: List[Mdl.TagValue] = []


class TagsUpdatedMsg(EngineMessage):
    tags: List[Mdl.TagValue] = []

# TODO: One possible way to supprt buffered messages. This would make it easier to persist
# the values for plot_log but maybe harder to insert in the realtime plot
class TagsBufferedMsg(EngineMessage):
    tags: List[Mdl.TagValue] = []
    tick_time: float


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
