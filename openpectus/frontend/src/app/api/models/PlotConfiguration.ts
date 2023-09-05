/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PlotColorRegion } from './PlotColorRegion';
import type { SubPlot } from './SubPlot';

export type PlotConfiguration = {
    process_value_names_to_annotate: Array<string>;
    color_regions: Array<PlotColorRegion>;
    sub_plots: Array<SubPlot>;
    x_axis_process_value_name: string;
};
