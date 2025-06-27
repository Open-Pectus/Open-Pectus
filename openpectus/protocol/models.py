from __future__ import annotations

import logging
import re

import openpectus.engine.models as EM
from pydantic import BaseModel, ConfigDict

from openpectus.lang.model.parser import ParserMethod, ParserMethodLine

logger = logging.getLogger(__name__)

SystemStateEnum = EM.SystemStateEnum
SystemTagName = EM.SystemTagName
TagDirection = EM.TagDirection
MethodStatusEnum = EM.MethodStatusEnum
EntryDataType = EM.EntryDataType

class ProtocolModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    def __str__(self) -> str:
        return f'{self.__class__.__name__}()'


class ReadingCommand(ProtocolModel):
    """ Represents a entry command for a reading. """
    command_id: str
    name: str
    command: str
    choice_names: list[str]

    def __str__(self) -> str:
        if len(self.choice_names):
            return (f'{self.__class__.__name__}(command_id="{self.command_id}", name="{self.name}", ' +
                    f'command="{self.command}", choice_names={self.choice_names})')
        else:
            return (f'{self.__class__.__name__}(command_id="{self.command_id}", name="{self.name}", ' +
                    f'command="{self.command}")')


class ReadingInfo(ProtocolModel):
    discriminator: str
    tag_name: str
    valid_value_units: list[str] | None
    entry_data_type: EntryDataType | None
    commands: list[ReadingCommand]
    command_options: dict[str, str] | None

    def __str__(self) -> str:
        if len(self.commands):
            return (f'{self.__class__.__name__}(tag_name="{self.tag_name}", valid_value_units={self.valid_value_units}, ' +
                    f'commands={self.commands})')
        else:
            return f'{self.__class__.__name__}(tag_name="{self.tag_name}", valid_value_units={self.valid_value_units})'

    def has_command_id(self, command_id: str) -> bool:
        for c in self.commands:
            if c.command_id == command_id:
                return True
        return False


class CommandInfo(ProtocolModel):
    """ Represents a uod command that may or may not be a reading entry command. """
    name: str
    docstring: str | None

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(name="{self.name}", docstring="{self.docstring}")'


TagValueType = float | int | str | None


class TagValue(ProtocolModel):
    name: str = ""
    tick_time: float
    value: TagValueType = None
    value_unit: str | None
    value_formatted: str | None = None
    direction: TagDirection = TagDirection.Unspecified
    simulated: bool | None = None

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(name="{self.name}", value="{self.value}", value_unit="{self.value_unit}", ' +
                f'direction="{self.direction}"), simulated="{self.simulated}"')


class RunLogLine(ProtocolModel):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: list[TagValue]
    end_values: list[TagValue]
    forcible: bool | None = None
    cancellable: bool | None = None
    forced: bool | None = None
    cancelled: bool | None = None

    def __str__(self) -> str:
        if self.cancelled:
            return (f'{self.__class__.__name__}(id="{self.id}", command_name="{self.command_name}", ' +
                    f'cancelled={self.cancelled})')
        elif self.forced:
            return (f'{self.__class__.__name__}(id="{self.id}", command_name="{self.command_name}", ' +
                    f'forced={self.forced})')
        elif self.progress is not None:
            return (f'{self.__class__.__name__}(id="{self.id}", command_name="{self.command_name}", ' +
                    f'progress={self.progress})')
        else:
            return f'{self.__class__.__name__}(id="{self.id}", command_name="{self.command_name}")'


class RunLog(ProtocolModel):
    lines: list[RunLogLine]

    def __str__(self) -> str:
        lines = [str(line) for line in self.lines]
        return f'{self.__class__.__name__}(lines={lines})'

    @staticmethod
    def empty() -> RunLog:
        return RunLog(lines=[])


class MethodLine(ProtocolModel):
    id: str
    content: str

    def __str__(self) -> str:
        return f'{self.__class__.__name__}(id="{self.id}", content="{self.content}")'


class Method(ProtocolModel):
    lines: list[MethodLine]

    def __str__(self) -> str:
        lines = [str(line) for line in self.lines]
        return f'{self.__class__.__name__}(lines={lines})'

    @staticmethod
    def empty() -> Method:
        return Method(lines=[])

    @staticmethod
    def from_pcode(pcode: str) -> Method:
        method = Method.empty()
        line_num: int = 1
        for line in pcode.splitlines():
            method.lines.append(MethodLine(id=f"id_{line_num}", content=line))
            line_num += 1
        return method

    def as_pcode(self) -> str:
        pcode = '\n'.join([line.content for line in self.lines])
        return pcode

    @staticmethod
    def from_numbered_pcode(pcode: str) -> Method:
        """ Creates a test method from specially formatted lines such as
            `'04 Mark: A'`
        and assigns the prefixed number as line id. """
        numbered_pcode_re = r'^(?P<number>\d+)\s(?P<content>.*)$'
        method = Method.empty()
        for line in pcode.splitlines():
            match = re.search(numbered_pcode_re, line)
            if match:
                method.lines.append(MethodLine(id=match.group("number"), content=match.group("content")))
            else:
                raise ValueError("Numbered method requires a two-digit number on all lines")
        return method

    def modify_to(self, pcode: str) -> Method:
        """ Edit the method code while maintaining line ids. Used to emulate method input
        coming from frontend where line ids are maintained in changed methods. """
        new_method = Method.from_pcode(pcode)
        for i, line in enumerate(new_method.lines):
            if i < len(self.lines):
                line.id = self.lines[i].id
        return new_method

    def to_parser_method(self) -> ParserMethod:
        return ParserMethod(
            lines=[ParserMethodLine(line.id, line.content) for line in self.lines]
        )


class MethodState(ProtocolModel):
    started_line_ids: list[str]
    executed_line_ids: list[str]
    injected_line_ids: list[str]

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(started_line_ids={self.started_line_ids}, ' +
                f'executed_line_ids={self.executed_line_ids}, injected_line_ids={self.injected_line_ids})')

    @staticmethod
    def empty() -> MethodState:
        return MethodState(started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


class ControlState(ProtocolModel):
    is_running: bool
    is_holding: bool
    is_paused: bool

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(is_running={self.is_running}, is_holding={self.is_holding}, ' +
                f'is_paused={self.is_paused})')


class Colors:
    C0 = "#1F77B4"
    C1 = "#FF7F0E"
    C2 = "#2CA02C"
    C3 = "#D62728"
    C4 = "#9467BD"
    C5 = "#8C564B"
    C6 = "#E377C2"
    C7 = "#7F7F7F"
    C8 = "#BCBD22"
    C9 = "#17BECF"

    Red = "#FF0000"
    Green = "#00FF00"


class PlotColorRegion(ProtocolModel):
    process_value_name: str
    # color string compatible with css e.g.: '#aa33bb', 'rgb(0,0,0)', 'rgba(0,0,0,0)', 'red'
    value_color_map: dict[str | int | float, str]


class PlotAxis(ProtocolModel):
    label: str
    process_value_names: list[str]
    y_max: int | float
    y_min: int | float
    color: str


class SubPlot(ProtocolModel):
    axes: list[PlotAxis]
    ratio: int | float


class PlotConfiguration(ProtocolModel):
    process_value_names_to_annotate: list[str]
    color_regions: list[PlotColorRegion]
    sub_plots: list[SubPlot]
    x_axis_process_value_names: list[str]

    @staticmethod
    def empty() -> PlotConfiguration:
        return PlotConfiguration(
            process_value_names_to_annotate=[],
            color_regions=[],
            sub_plots=[],
            x_axis_process_value_names=[]
        )


class ErrorLogEntry(ProtocolModel):
    message: str
    created_time: float
    severity: int

    def __str__(self) -> str:
        return (f'{self.__class__.__name__}(message="{self.message}", created_time={self.created_time}, ' +
                f'severity={self.severity})')


class ErrorLog(ProtocolModel):
    entries: list[ErrorLogEntry]

    def __str__(self) -> str:
        entries = [str(entry) for entry in self.entries]
        return f'{self.__class__.__name__}(entries={entries})'

    @staticmethod
    def empty() -> ErrorLog:
        return ErrorLog(entries=[])


class TagDefinition(ProtocolModel):
    name: str
    unit: str | None = None


class CommandDefinition(ProtocolModel):
    name: str
    """ Command name, eg. 'Wait' """
    validator: str | None
    """ Serialization of validator or None for no validation"""
    docstring: str | None
    """ Command docstring """


class UodDefinition(ProtocolModel):
    commands: list[CommandDefinition]
    """ Uod commands """
    system_commands: list[CommandDefinition]
    """ System commands """
    tags: list[TagDefinition]
    """ System and uod tags """
