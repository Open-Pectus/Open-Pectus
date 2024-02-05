from __future__ import annotations

import logging
from enum import StrEnum, auto
from typing import List

from pydantic import BaseModel

logger = logging.getLogger(__name__)


class ProtocolModel(BaseModel):
    class Config:
        smart_union = True
        orm_mode = True


class ReadingCommand(ProtocolModel):
    name: str
    command: str


class ReadingInfo(ProtocolModel):
    tag_name: str
    valid_value_units: List[str] | None
    commands: List[ReadingCommand]


TagValueType = float | int | str | None


class SystemTagName(StrEnum):
    run_time = auto()
    system_state = auto()
    run_id = auto()


class TagValue(ProtocolModel):
    name: str = ""
    tick_time: float
    value: TagValueType = None
    value_unit: str | None


class RunLogLine(ProtocolModel):
    id: str
    command_name: str
    start: float
    end: float | None
    progress: float | None  # between 0 and 1
    start_values: List[TagValue]
    end_values: List[TagValue]


class RunLog(ProtocolModel):
    lines: List[RunLogLine]


class MethodLine(ProtocolModel):
    id: str
    content: str


class Method(ProtocolModel):
    lines: List[MethodLine]

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
    started_line_ids: List[str]
    executed_line_ids: List[str]
    injected_line_ids: List[str]

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
    process_value_names: List[str]
    y_max: int | float
    y_min: int | float
    color: str


class SubPlot(ProtocolModel):
    axes: List[PlotAxis]
    ratio: int | float


class PlotConfiguration(ProtocolModel):
    process_value_names_to_annotate: List[str]
    color_regions: List[PlotColorRegion]
    sub_plots: List[SubPlot]
    x_axis_process_value_names: List[str]

    @staticmethod
    def empty() -> PlotConfiguration:
        return PlotConfiguration(process_value_names_to_annotate=[], color_regions=[], sub_plots=[], x_axis_process_value_names=[])
