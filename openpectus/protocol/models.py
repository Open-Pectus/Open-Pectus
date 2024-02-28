from __future__ import annotations

import logging
from enum import StrEnum, auto

import openpectus.engine.models as EM
from pydantic import BaseModel

logger = logging.getLogger(__name__)

SystemStateEnum = EM.SystemStateEnum
SystemTagName = EM.SystemTagName
TagDirection = EM.TagDirection


class ProtocolModel(BaseModel):
    class Config:
        smart_union = True
        orm_mode = True


class ReadingCommand(ProtocolModel):
    name: str
    command: str


class ReadingInfo(ProtocolModel):
    tag_name: str
    valid_value_units: list[str] | None
    commands: list[ReadingCommand]


TagValueType = float | int | str | None


class TagValue(ProtocolModel):
    name: str = ""
    tick_time: float
    value: TagValueType = None
    value_unit: str | None
    direction: EM.TagDirection = TagDirection.UNSPECIFIED


class RunLogLine(ProtocolModel):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: list[TagValue]
    end_values: list[TagValue]


class RunLog(ProtocolModel):
    lines: list[RunLogLine]


class MethodLine(ProtocolModel):
    id: str
    content: str


class Method(ProtocolModel):
    lines: list[MethodLine]

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


class MethodState(ProtocolModel):
    started_line_ids: list[str]
    executed_line_ids: list[str]
    injected_line_ids: list[str]

    @staticmethod
    def empty() -> MethodState:
        return MethodState(started_line_ids=[], executed_line_ids=[], injected_line_ids=[])


class ControlState(ProtocolModel):
    is_running: bool
    is_holding: bool
    is_paused: bool



class PlotColorRegion(ProtocolModel):
    process_value_name: str
    value_color_map: dict[str | int | float, str]  # color string compatible with css e.g.: '#aa33bb', 'rgb(0,0,0)', 'rgba(0,0,0,0)', 'red'


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
        return PlotConfiguration(process_value_names_to_annotate=[], color_regions=[], sub_plots=[], x_axis_process_value_names=[])

class ErrorLogEntry(ProtocolModel):
    message: str
    created_time: float
    severity: int

class ErrorLog(ProtocolModel):
    entries: list[ErrorLogEntry]

    @staticmethod
    def empty() -> ErrorLog:
        return ErrorLog(entries=[])
