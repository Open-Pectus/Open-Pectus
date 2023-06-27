/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { PlotColorRegion } from './PlotColorRegion';
import type { SubPlot } from './SubPlot';

export type PlotConfiguration = {
    color_regions: Array<PlotColorRegion>;
    sub_plots: Array<SubPlot>;
};
