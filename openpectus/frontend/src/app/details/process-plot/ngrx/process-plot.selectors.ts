import { createFeatureSelector, createSelector } from '@ngrx/store';
import { Layout } from 'plotly.js';
import { LayoutAxis, PlotData } from 'plotly.js-basic-dist-min';
import { SubPlot } from '../../../api';
import { DetailsSelectors } from '../../ngrx/details.selectors';
import { PlotlyDefaults } from '../plotly-defaults';
import { processPlotSlice, ProcessPlotState } from './process-plot.reducer';

export class ProcessPlotSelectors {
  static featureSelector = createFeatureSelector<ProcessPlotState>(processPlotSlice.name);
  static plotConfiguration = createSelector(this.featureSelector, state => state.plotConfiguration);
  static processValuePlots = createSelector(DetailsSelectors.processValuesLog, this.plotConfiguration, (processValueLog, plotConfiguration) => {
    if(plotConfiguration === undefined) return [];
    return plotConfiguration.sub_plots.flatMap((subPlot, subPlotIndex) => {
      return subPlot.axes.flatMap((axis, axisIndex) => {
        return axis.process_value_names.map(processValueName => {
          return {
            x: processValueLog.map((_, index) => index), // TODO: should be timestamp
            y: processValueLog.map(processValues => processValues.find(processValue => processValue.name === processValueName)?.value),
            yaxis: 'y' + this.mapAxisIndex(subPlotIndex),
            type: 'scatter',
            xaxis: 'x',
            name: processValueName,
          } as Partial<PlotData>;
        });
      });
    });
  });
  static processPlotLayout = createSelector(this.plotConfiguration, (plotConfiguration) => {
    if(plotConfiguration === undefined) return undefined;
    return {
      grid: {
        rows: plotConfiguration.sub_plots.length,
        columns: 1,
        subplots: plotConfiguration.sub_plots.map((subPlot, subPlotIndex) => {
          return subPlot.axes.map((axis, axisIndex) => `xy${(this.mapAxisIndex(axisIndex + subPlotIndex))}`);
        }),
        // yaxes: this.convertToAxes(plotConfiguration.sub_plots), // plotConfiguration?.sub_plots.flatMap(subPlot => this.convertToAxes(subPlot.axes.map(axis => axis.label)))
        roworder: 'top to bottom',
        ygap: 10,
        uirevision: 'true',
        autosize: true,
      },
    } as unknown as Partial<Layout>; // type of subplots is a lie according to documentation
  });

  private static mapAxisIndex(axisIndex: number) {
    return axisIndex > 0 ? axisIndex + 1 : '';
  }

  private static convertToAxes(subPlots: SubPlot[]) {
    const object = {};
    subPlots.forEach((subPlot, subPlotIndex) => {
      subPlot.axes.forEach((axis, axisIndex) => {
        Object.assign(object, {
          ['yaxis' + this.mapAxisIndex(axisIndex + subPlotIndex)]: {
            title: axis.label,
            side: (axisIndex > 0 ? 'right' : 'left'),
            overlaying: axisIndex > 0 ? 'y' : 'free',
            anchor: axisIndex > 1 ? 'free' : undefined,
            position: axisIndex > 1 ? 1 : undefined,
            titlefont: {color: PlotlyDefaults.colors[subPlotIndex]},
            tickfont: {color: PlotlyDefaults.colors[subPlotIndex]},
            range: [axis.y_min, axis.y_max],
          } as Partial<LayoutAxis>,
        });
      });
    });
    return object;
  }
}
