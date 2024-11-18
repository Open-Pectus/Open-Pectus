import math
from time import time
from typing import Any

from openpectus.engine.uod_builder_api import (
    UnitOperationDefinitionBase, UodBuilder, UodCommand,
    as_float,
    tags,
    PlotConfiguration, SubPlot, PlotAxis, PlotColorRegion,
    RegexNumber,
    HardwareLayerBase, Register, RegisterDirection  # special import required by custom hardware, DemoHardware
)


def create() -> UnitOperationDefinitionBase:
    builder = UodBuilder()
    # use this logger to send warnings/errors to the frontend error log
    # logger = builder.get_logger()

    def reset(cmd: UodCommand, **kvargs) -> None:
        count = cmd.get_iteration_count()
        max_ticks = 100
        if count == 0:
            cmd.context.tags.get("Reset").set_value("Reset", time())
            cmd.context.hwl.reset_FT01()  # type: ignore
        elif count > max_ticks:
            cmd.context.tags.get("Reset").set_value("N/A", time())
            cmd.set_complete()
        else:
            progress = count/max_ticks
            cmd.set_progress(progress)

    def test_cmd(cmd: UodCommand, value):
        print("test_cmd executing with arg: " + value)
        fval = as_float(value)
        if fval is None:
            # raising ValueError will display the error to the user
            raise ValueError("value must be a number")
        cmd.context.tags.get("TestInt").set_value(value, time())
        cmd.set_complete()

    def cmd_regex(cmd: UodCommand, number, number_unit=None):
        # optional arg is ok when regex's named groups do not include it
        print("cmd_regex executing with number: " + str(number))
        print("and number_unit: " + str(number_unit))
        cmd.set_complete()

    def test_percentage(cmd: UodCommand, number, number_unit):
        # Note: When using RegexNumber, the number argument is still a
        # string but it will always support conversion to float
        number = float(number)
        cmd.context.tags.get("TestPercentage").set_value(number, time())
        cmd.set_complete()

    def get_plot_configuration() -> PlotConfiguration:
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
        .with_author("Demo Author", "demo@openpectus.org")
        .with_filename(__file__)
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
        .with_tag(tags.ReadingTag("Time", unit=None))
        .with_tag(tags.Tag("TestInt", value="42"))
        .with_tag(tags.Tag("TestFloat", value=9.87, unit="kg"))
        .with_tag(tags.Tag("TestString", value="test"))
        .with_tag(tags.SelectTag("Reset", value="N/A", unit=None, choices=['Reset', "N/A"]))
        .with_tag(tags.Tag("TestPercentage", value=34.87, unit="%"))
        .with_command(name="Reset", exec_fn=reset)
        .with_command(name="TestInt", exec_fn=test_cmd)
        .with_process_value(tag_name="Run Time")
        .with_process_value(tag_name="FT01")
        .with_process_value_entry(tag_name="TestInt")
        .with_process_value_entry(tag_name="TestFloat", execute_command_name="TestInt")
        .with_process_value_choice(tag_name="TestString", command_options={'A': 'Mark: A', 'B': 'Mark: B'})
        .with_process_value(tag_name="FT02")
        .with_process_value(tag_name="Category")
        .with_process_value(tag_name="Time")
        .with_process_value_choice(tag_name="Reset", command_options={'Reset': 'Reset'})
        .with_process_value(tag_name="System State")
        .with_process_value(tag_name="TestPercentage")
        .with_command_regex_arguments(
            name="CmdWithRegexArgs",
            arg_parse_regex=RegexNumber(units=None),
            exec_fn=cmd_regex)
        .with_command_regex_arguments(
            name="TestPercentage",
            arg_parse_regex=RegexNumber(units=['%']),
            exec_fn=test_percentage)
        .with_process_value_entry(tag_name="TestPercentage")

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
        # if r.name == "Reset":
        #     return
        # print(f"DemoHardware: Wrote value '{value}' to register '{r.name}'")
