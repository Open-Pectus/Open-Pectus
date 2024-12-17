from typing import Sequence

import openpectus.protocol.messages as Msg
import openpectus.protocol.models as Mdl


# Note: These are the messages sent by EngineDispatcher and handled by AggregatorMessageHandlers.

class EngineMessage(Msg.MessageBase):
    sequence_number: int = -1
    engine_id: str = ''

    @property
    def ident(self) -> str:
        return f"seq: {self.sequence_number: >3}, type: {type(self).__name__}"


class EngineControlMessage(EngineMessage):
    pass


class EngineDataMessage(EngineMessage):
    pass


class PingMsg(EngineControlMessage):
    pass


class RegisterEngineMsg(Msg.MessageBase):
    """ Doesn't extend EngineMessage, because we don't have the engine_id yet """
    computer_name: str
    uod_name: str
    uod_author_name: str
    uod_author_email: str
    uod_filename: str
    location: str
    engine_version: str
    # uod file hash, file change date

    sequence_number: int = -2

    @property
    def ident(self) -> str:
        return f"seq: {self.sequence_number: >3}, type: {type(self).__name__}"


class UodInfoMsg(EngineMessage):
    readings: list[Mdl.ReadingInfo]
    commands: list[Mdl.CommandInfo]
    plot_configuration: Mdl.PlotConfiguration
    hardware_str: str
    required_roles: set[str]
    data_log_interval_seconds: float


class TagsUpdatedMsg(EngineMessage):
    tags: list[Mdl.TagValue] = []

# TODO: One possible way to supprt buffered messages. This would make it easier to persist
# the values for plot_log but maybe harder to insert in the realtime plot
class TagsBufferedMsg(EngineMessage):
    tags: list[Mdl.TagValue] = []
    tick_time: float


class RunLogMsg(EngineMessage):
    id: str
    run_id: str
    runlog: Mdl.RunLog


class ErrorLogMsg(EngineMessage):
    log: Mdl.ErrorLog


class MethodMsg(EngineMessage):
    method: Mdl.Method


class MethodStateMsg(EngineMessage):
    method_state: Mdl.MethodState


class ControlStateMsg(EngineMessage):
    control_state: Mdl.ControlState


class RunStartedMsg(EngineMessage):
    run_id: str
    started_tick: float


class RunStoppedMsg(EngineMessage):
    run_id: str
    runlog: Mdl.RunLog
    method: Mdl.Method


def print_sequence_range(messages: Sequence[EngineMessage]) -> str:
    """ print message sequence numbers in concise format"""
    if len(messages) == 0:
        return ""
    msgs_sorted: list[EngineMessage] = sorted(messages, key=lambda x: x.sequence_number)
    ranges = []
    range_start: int | None = None

    prev: EngineMessage | None = None
    for i, msg in enumerate(msgs_sorted):
        if i == 0:
            prev = msg
            range_start = msg.sequence_number
            continue
        if msg.sequence_number != prev.sequence_number + 1:  # type: ignore
            ranges.append((range_start, prev.sequence_number))  # type: ignore
            range_start = msg.sequence_number
        prev = msg

    if range_start is not None and range_start <= msgs_sorted[-1].sequence_number:
        ranges.append((range_start, msgs_sorted[-1].sequence_number))

    out = []
    for range in ranges:
        if range[0] == range[1]:
            out.append(str(range[0]))
        else:
            out.append(f"{range[0]}-{range[1]}")
    return ",".join(out)
