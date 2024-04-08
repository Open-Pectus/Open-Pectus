import math
from time import time
from typing import Any

from openpectus.engine.hardware import HardwareLayerBase, Register, RegisterDirection
from openpectus.lang.exec import readings as R
import openpectus.lang.exec.tags_impl as tags
from openpectus.lang.exec.uod import UnitOperationDefinitionBase, UodCommand, UodBuilder
from openpectus.protocol.models import PlotConfiguration, SubPlot, PlotAxis, PlotColorRegion


def create_demo_uod() -> UnitOperationDefinitionBase:
    builder = UodBuilder()
    logger = builder.get_logger()

    def reset(cmd: UodCommand, _) -> None:
        count = cmd.get_iteration_count()
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time())
            cmd.context.hwl.reset_FT01()  # type: ignore
        elif count == 4:
            cmd.context.tags.get("Reset").set_value("N/A", time())
            cmd.set_complete()

    def get_plot_configuration() -> PlotConfiguration:
        logger.warn('FOR TESTING PURPOSES: getting plot configuration') # TODO: delete this when we have actual uod warnings and errors to test with
        return PlotConfiguration(
            color_regions=[
                PlotColorRegion(
                    process_value_name='Category',
                    value_color_map={'Rising': '#66ff6633', 'Falling': '#6666ff33'})
            ],
            sub_plots=[SubPlot(
                axes=[PlotAxis(
                    label='FT01',
                    process_value_names=['FT01'],
                    y_max=20,
                    y_min=0,
                    color='#ff0000',
                ), PlotAxis(
                    label='FT02',
                    process_value_names=['FT02'],
                    y_max=20,
                    y_min=0,
                    color='#0000ff',
                )],
                ratio=1
            )],
            process_value_names_to_annotate=['Category'],
            x_axis_process_value_names=['Time']
        )

    return (
        builder
        .with_instrument("DemoUod")
        .with_hardware(DemoHardware())
        .with_location("Demo location")
        .with_hardware_register("FT01", RegisterDirection.Read, path='Objects;2:System;2:FT01')
        .with_hardware_register("FT02", RegisterDirection.Read, path='Objects;2:System;2:FT02')
        .with_hardware_register("Category", RegisterDirection.Read, path='Objects;2:System;2:Category')
        .with_hardware_register("Time", RegisterDirection.Read)
        .with_hardware_register("Reset", RegisterDirection.Both, path='Objects;2:System;2:RESET',
                                from_tag=lambda x: 1 if x == 'Reset' else 0,
                                to_tag=lambda x: "Reset" if x == 1 else "N/A")
        .with_tag(tags.ReadingTag("FT01", "L/h"))
        .with_tag(tags.ReadingTag("FT02", "L/h"))
        .with_tag(tags.ReadingTag("Category"))
        .with_tag(tags.ReadingTag("Time"))
        .with_tag(tags.SelectTag("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))
        .with_command(UodCommand.builder().with_name("Reset").with_exec_fn(reset))
        .with_process_value(R.Reading(tag_name="Run Time"))
        .with_process_value(R.Reading(tag_name="FT01"))
        .with_process_value(R.Reading(tag_name="FT02"))
        .with_process_value(R.Reading(tag_name="Category"))
        .with_process_value(R.Reading(tag_name="Time"))
        .with_process_value(R.Reading(tag_name="Reset"))
        .with_process_value(R.Reading(tag_name="System State"))
        .with_plot_configuration(get_plot_configuration())
        .build()
    )


class DemoHardware(HardwareLayerBase):
    """ Simulation hardware. """

    def __init__(self) -> None:
        super().__init__()
        self.start_time: float = time()

    def reset_FT01(self):
        self.start_time = time()

    def read(self, r: Register) -> Any:
        if r.name == "FT01":
            elapsed_seconds = time() - self.start_time
            half_minutes = elapsed_seconds / 30
            return int(10 * (math.sin(half_minutes) + 1))
        elif r.name == "FT02":
            elapsed_seconds = time() - self.start_time
            half_minutes = elapsed_seconds / 30
            return 10 * (math.sin(half_minutes) + 1)
        elif r.name == "Time":
            return time() - self.start_time
        elif r.name == 'Category':
            elapsed_seconds = time() - self.start_time
            half_minutes = elapsed_seconds / 30
            return 'Rising' if math.cos(half_minutes) > 0 else 'Falling'

    def write(self, value: Any, r: Register):
        pass

    def connect(self):
        ...

    def disconnect(self):
        ...
