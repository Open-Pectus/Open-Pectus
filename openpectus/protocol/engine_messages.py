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

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number})'


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
    secret: str = ""
    # uod file hash, file change date

    sequence_number: int = -2

    @property
    def ident(self) -> str:
        return f"seq: {self.sequence_number: >3}, type: {type(self).__name__}"

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(computer_name="{self.computer_name}", ' +
                f'uod_name="{self.uod_name}", location="{self.location}")')


class UodInfoMsg(EngineMessage):
    readings: list[Mdl.ReadingInfo]
    commands: list[Mdl.CommandInfo]
    uod_definition: Mdl.UodDefinition
    plot_configuration: Mdl.PlotConfiguration
    hardware_str: str
    required_roles: set[str]
    data_log_interval_seconds: float

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'readings={self.readings}, commands={self.commands}, hardware_str="{self.hardware_str}", ' +
                f'required_roles={self.required_roles}, data_log_interval_seconds={self.data_log_interval_seconds})')


class TagsUpdatedMsg(EngineMessage):
    tags: list[Mdl.TagValue] = []

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'tags={self.tags})')

# TODO: One possible way to supprt buffered messages. This would make it easier to persist
# the values for plot_log but maybe harder to insert in the realtime plot
class TagsBufferedMsg(EngineMessage):
    tags: list[Mdl.TagValue] = []
    tick_time: float

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'tags={self.tags}, tick_time={self.tick_time})')


class RunLogMsg(EngineMessage):
    id: str
    run_id: str
    runlog: Mdl.RunLog

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'id="{self.id}", run_id="{self.run_id}", runlog={self.runlog})')


class ErrorLogMsg(EngineMessage):
    log: Mdl.ErrorLog

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'log={self.log})')


class MethodMsg(EngineMessage):
    method: Mdl.Method

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'method={self.method})')


class MethodStateMsg(EngineMessage):
    method_state: Mdl.MethodState

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'method_state={self.method_state})')


class ControlStateMsg(EngineMessage):
    control_state: Mdl.ControlState

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'control_state={self.control_state})')


class RunStartedMsg(EngineMessage):
    run_id: str
    started_tick: float

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'run_id="{self.run_id}", started_tick={self.started_tick})')


class RunStoppedMsg(EngineMessage):
    run_id: str
    runlog: Mdl.RunLog
    method_state: Mdl.MethodState

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(engine_id="{self.engine_id}", sequence_number={self.sequence_number}, ' +
                f'run_id="{self.run_id}", runlog={self.runlog}, method_state="{self.method_state}"')


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
