
from time import time
from openpectus.engine.uod_builder_api import (
    UnitOperationDefinitionBase, UodCommand, UodBuilder,
    tags, RegisterDirection,
    PlotConfiguration, SubPlot, PlotAxis, PlotColorRegion
)


def create() -> UnitOperationDefinitionBase:
    builder = UodBuilder()

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

    def reset(cmd: UodCommand, value):
        cmd.context.tags["RESET"].set_value(1.0, time())

        # we don't support this. could be nice, though
        # for i in range(10):
        #     cmd.set_progress(.1 * i)
        #     yield

        cmd.set_complete()

        # TODO consider reset behavior:
        # Server reads the RESET register and executes its reset if non-zero and immideately sets the register value
        # bath to zero. This does not really match any of our register directions.

        # This does work but causes an extra reset from server
        # if cmd.get_iteration_count() > 0:
        #     cmd.set_complete()

    return (
        builder
        .with_instrument("Opcua-Test")
        .with_author("Demo Author", "demo@openpectus.org")
        .with_filename(__file__)
        .with_hardware_opcua(host="opc.tcp://127.0.0.1:48400")
        .with_location("Test location")
        .with_hardware_register("RESET", RegisterDirection.Both, path='Objects/2:System/2:RESET')
        .with_hardware_register("VA01", RegisterDirection.Read, path='Objects/2:System/2:VA01')
        .with_hardware_register("VA02", RegisterDirection.Read, path='Objects/2:System/2:VA02')
        .with_hardware_register("TT01", RegisterDirection.Read, path='Objects/2:System/2:TT01')
        .with_hardware_register("FT01", RegisterDirection.Read, path='Objects/2:System/2:FT01')
        .with_hardware_register("PU01", RegisterDirection.Read, path='Objects/2:System/2:PU01')

        .with_tag(tags.ReadingTag(name="RESET"))
        .with_tag(tags.ReadingTag(name="VA01"))
        .with_tag(tags.ReadingTag(name="VA02"))
        .with_tag(tags.ReadingTag(name="TT01"))  # unit="degC"
        .with_tag(tags.ReadingTag(name="FT01"))
        .with_tag(tags.ReadingTag(name="PU01"))

        .with_command("RESET", exec_fn=reset)

        .with_process_value("VA01")
        .with_process_value("VA02")
        .with_process_value("TT01")
        .with_process_value("FT01")
        .with_process_value("PU01")
        .with_process_value_choice(tag_name="RESET", command_options={"Reset": "RESET"})

        .with_plot_configuration(get_plot_configuration())
        .build()
    )
